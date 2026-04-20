import asyncio
import json
import base64
import pyaudio
import websockets
import threading
import numpy as np
from config import OPENAI_API_KEY, REALTIME_WS_URL, AUDIO_CHANNELS, AUDIO_SAMPLE_RATE, AUDIO_CHUNK

class RealtimeVoiceClient:
    def __init__(self, on_command_cb):
        self.on_command_cb = on_command_cb
        self._stop = threading.Event()
        self.thread = None
        self.is_listening = False
        self.play_audio = False  # True = AI assistant mode, False = command-only mode

    def start(self):
        self._stop.clear()
        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self._stop.set()
        if self.thread:
            self.thread.join(timeout=2.0)

    def _run_async_loop(self):
        asyncio.run(self._connect_and_run())

    async def _connect_and_run(self):
        if not OPENAI_API_KEY:
            print("WARNING: OPENAI_API_KEY not found in .env. Voice commands disabled.")
            return

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1",
        }
        
        while not self._stop.is_set():
            try:
                async with websockets.connect(REALTIME_WS_URL, additional_headers=headers) as ws:
                    await ws.send(json.dumps({
                        "type": "session.update",
                        "session": {
                            "modalities": ["text", "audio"],
                            "voice": "shimmer",
                            "input_audio_format": "pcm16",
                            "output_audio_format": "pcm16",
                            "turn_detection": {"type": "server_vad"},
                            "instructions": (
                                "You are AeroControl AI. You have two modes:\n\n"
                                "MODE 1 - COMMAND: If the user does NOT start with a greeting, "
                                "find the EXACT match from this command list and output ONLY that text (nothing else, no audio): "
                                "['next slide', 'previous slide', 'mute', 'unmute', 'volume up', 'volume down', "
                                "'full screen', 'escape', 'next track', 'previous track', 'play', 'pause', 'set volume to <number>']. "
                                "If no command matches, output nothing.\n\n"
                                "MODE 2 - ASSISTANT: If the user STARTS with a greeting word "
                                "(hi, hello, hey, salom, assalomu alaykum, привет, здравствуй, or any greeting in any language), "
                                "switch to friendly assistant mode. Respond naturally and helpfully. "
                                "ALWAYS reply in the EXACT SAME language the user spoke. "
                                "Prefix your text output with 'CONVERSATION: ' so the system knows to play your voice."
                            ),
                        }
                    }))
                    
                    await asyncio.gather(
                        self._send_audio(ws),
                        self._receive_events(ws),
                    )
            except Exception as e:
                print(f"Voice client error: {e}. Retrying in 2 seconds...")
                await asyncio.sleep(2.0)

    async def _send_audio(self, ws):
        pa = pyaudio.PyAudio()
        try:
            stream = pa.open(
                format=pyaudio.paInt16,
                channels=AUDIO_CHANNELS,
                rate=AUDIO_SAMPLE_RATE,
                input=True, 
                frames_per_buffer=AUDIO_CHUNK,
            )
            
            while not self._stop.is_set():
                try:
                    data = stream.read(AUDIO_CHUNK, exception_on_overflow=False)
                    if self.is_listening:
                        b64 = base64.b64encode(data).decode()
                        await ws.send(json.dumps({
                            "type": "input_audio_buffer.append",
                            "audio": b64,
                        }))
                except IOError as e:
                    pass
                await asyncio.sleep(0)
                
            stream.stop_stream()
            stream.close()
        except Exception as e:
            pass
        finally:
            pa.terminate()

    async def _receive_events(self, ws):
        # Speaker output stream for playing AI voice responses
        pa = pyaudio.PyAudio()
        speaker = None
        try:
            speaker = pa.open(
                format=pyaudio.paInt16,
                channels=AUDIO_CHANNELS,
                rate=AUDIO_SAMPLE_RATE,
                output=True,
                frames_per_buffer=AUDIO_CHUNK,
            )
        except Exception as e:
            print(f"[Voice] Could not open speaker: {e}")
        
        try:
            async for raw in ws:
                if self._stop.is_set(): 
                    break
                
                event = json.loads(raw)
                etype = event.get('type', '')
                
                # Play audio chunks from the AI response (only in assistant mode)
                if etype == 'response.audio.delta':
                    if self.play_audio:
                        audio_b64 = event.get('delta', '')
                        if audio_b64 and speaker:
                            try:
                                audio_bytes = base64.b64decode(audio_b64)
                                speaker.write(audio_bytes)
                            except Exception:
                                pass
                
                # Handle text responses (commands or conversation marker)
                elif etype == 'response.output_item.done':
                    for item in event.get('item', {}).get('content', []):
                        if item.get('type') == 'text':
                            text = item.get('text', '').strip()
                            if text:
                                if text.lower().startswith('conversation:'):
                                    self.play_audio = True
                                    clean = text[len('conversation:'):].strip()
                                    print(f"[Voice AI] Assistant reply: \"{clean}\"")
                                else:
                                    self.play_audio = False
                                    print(f"[Voice AI] Command: {text}")
                                    self.on_command_cb(text)
                        elif item.get('type') == 'audio':
                            transcript = item.get('transcript', '').strip()
                            if transcript:
                                print(f"[Voice AI] Said: \"{transcript}\"")
                                
                elif etype == 'error':
                    print(f"[Voice API ERROR] {event.get('error', {}).get('message', '')}")
        finally:
            if speaker:
                speaker.stop_stream()
                speaker.close()
            pa.terminate()
