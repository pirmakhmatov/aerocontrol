import pyaudio
pa = pyaudio.PyAudio()
try:
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=24000, input=True, frames_per_buffer=2400)
    print("SUCCESS: Mic opened")
    stream.close()
except Exception as e:
    print(f"ERROR: {e}")
pactl = __import__('os').system('which pactl > /dev/null')
amixer = __import__('os').system('which amixer > /dev/null')
print(f"pactl={pactl}, amixer={amixer}")
