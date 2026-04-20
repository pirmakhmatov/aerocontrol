import asyncio
import json
import base64
import pyaudio
import websockets
import threading
import numpy as np
from config import OPENAI_API_KEY, REALTIME_WS_URL, AUDIO_CHANNELS, AUDIO_SAMPLE_RATE, AUDIO_CHUNK

COMMAND_LIST = [
    'next slide', 'previous slide', 'mute', 'unmute',
    'volume up', 'volume down', 'full screen', 'escape',
    'next track', 'previous track', 'play', 'pause',
    'set volume to', 'volume',
]

PROMPT_COMMAND_ONLY = (
    "You are AeroControl voice command executor. "
    "STRICT RULES — no exceptions:\n"
    "1. Listen to what the user says.\n"
    "2. Match it to ONE of these exact commands (case-insensitive): "
    "next slide | previous slide | mute | unmute | volume up | volume down | "
    "full screen | escape | next track | previous track | play | pause | set volume to <number>.\n"
    "3. Output ONLY the matched command as a TEXT response. No other words, no explanation, no punctuation.\n"
    "4. If nothing matches, output absolutely nothing.\n"
    "DO NOT have a conversation. DO NOT say anything extra. COMMAND TEXT ONLY."
)

PROMPT_ASSISTANT = (
    "You are AeroControl AI assistant. You have two modes:\n\n"
    "MODE 1 - COMMAND: If the user says a command (next slide, previous slide, mute, unmute, "
    "volume up, volume down, full screen, escape, next track, previous track, play, pause, "
    "set volume to <number>), output ONLY that matched command as a TEXT item. No other words.\n\n"
    "MODE 2 - CONVERSATION: If the user says anything else (questions, greetings, requests), "
    "respond helpfully and naturally. ALWAYS reply in the EXACT SAME language the user spoke. "
    "Prefix your text response with 'CONVERSATION: ' so the system knows to speak your reply aloud."
)


class RealtimeVoiceClient:
    def __init__(self, on_command_cb):
        self.on_command_cb = on_command_cb
        self._stop = threading.Event()
        self.thread = None
        self.is_listening = False
        self.play_audio = False      # True = AI assistant mode, False = command-only mode
        self._pending_response = False  # Grace flag: keep receiving after mic off
        self._current_mode = "COMMAND"  # "COMMAND" or "ASSISTANT"
        self._ws = None              # Reference to active websocket for live session updates
        self._loop = None            # The asyncio event loop for this client

    def start(self):
        self._stop.clear()
        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self._stop.set()
        if self.thread:
            self.thread.join(timeout=2.0)

    def set_mode(self, mode: str):
        """
        Call from any thread to switch the AI session mode.
        mode: "COMMAND" → strict command executor
              "ASSISTANT" → conversational AI + commands
        """
        if mode == self._current_mode:
            return
        self._current_mode = mode
        self.play_audio = (mode == "ASSISTANT")
        if self._ws and self._loop and not self._loop.is_closed():
            asyncio.run_coroutine_threadsafe(self._send_session_update(), self._loop)

    def _run_async_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._connect_and_run())

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
                    self._ws = ws
                    await self._send_session_update()
                    
                    await asyncio.gather(
                        self._send_audio(ws),
                        self._receive_events(ws),
                    )
            except Exception as e:
                self._ws = None
                print(f"Voice client error: {e}. Retrying in 2 seconds...")
                await asyncio.sleep(2.0)

    async def _send_session_update(self):
        """Push a session.update to the active WS to change the AI persona/instructions."""
        if not self._ws:
            return
        prompt = PROMPT_COMMAND_ONLY if self._current_mode == "COMMAND" else PROMPT_ASSISTANT
        try:
            await self._ws.send(json.dumps({
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "voice": "shimmer",
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "turn_detection": {"type": "server_vad"},
                    "instructions": prompt,
                }
            }))
            print(f"[Voice] Session mode → {self._current_mode}")
        except Exception as e:
            print(f"[Voice] Session update failed: {e}")

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
                    # Send audio while listening OR while waiting for pending response
                    if self.is_listening or self._pending_response:
                        b64 = base64.b64encode(data).decode()
                        await ws.send(json.dumps({
                            "type": "input_audio_buffer.append",
                            "audio": b64,
                        }))
                except IOError:
                    pass
                await asyncio.sleep(0)
                
            stream.stop_stream()
            stream.close()
        except Exception:
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
                # Reset play_audio state to match mode at the start of every response
                if etype == 'response.created':
                    self.play_audio = (self._current_mode == "ASSISTANT")

                # Play audio chunks from the AI response (only in assistant mode)
                elif etype == 'response.audio.delta':
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
                    command_dispatched = False
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
                                    command_dispatched = True
                        elif item.get('type') == 'audio':
                            transcript = item.get('transcript', '').strip()
                            if transcript:
                                print(f"[Voice AI] Said: \"{transcript}\"")
                                # Fallback: if no text command was dispatched, try the audio transcript
                                if not command_dispatched and not self.play_audio:
                                    t = transcript.lower().strip().rstrip('.')
                                    matched = next((cmd for cmd in COMMAND_LIST if cmd in t or t in cmd), None)
                                    if matched:
                                        print(f"[Voice AI] Fallback transcript command: {matched} (Full: {transcript})")
                                        self.on_command_cb(transcript)
                                        command_dispatched = True
                    self._pending_response = False
                                
                elif etype == 'error':
                    print(f"[Voice API ERROR] {event.get('error', {}).get('message', '')}")
        finally:
            if speaker:
                speaker.stop_stream()
                speaker.close()
            pa.terminate()
