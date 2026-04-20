import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REALTIME_WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview"

CAM_INDEX = 0
CAM_WIDTH = 1280
CAM_HEIGHT = 720

PINCH_THRESHOLD = 0.05
SWIPE_VELOCITY_THRESHOLD = 0.03

AUDIO_SAMPLE_RATE = 24000
AUDIO_CHANNELS = 1
AUDIO_CHUNK = 2400
