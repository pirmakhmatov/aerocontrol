<p align="center">
  <h1 align="center">✋ AeroControl</h1>
  <p align="center">
    <strong>Touchless gesture & voice control for your desktop</strong><br>
    Control presentations, media, volume, and more — entirely hands-free.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/mediapipe-hand_tracking-orange?logo=google" />
  <img src="https://img.shields.io/badge/openai-realtime_voice-412991?logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/platform-linux-lightgrey?logo=linux" />
</p>

---

## 🎯 What is AeroControl?

AeroControl is a background daemon that uses your webcam and AI to recognize hand gestures and voice commands in real-time. It runs silently in the system tray and lets you control your computer without touching the keyboard or mouse.

**Built for the April 2026 AI Hackathon** at the Qarshi branch of the Presidential School.

### ✨ Key Features

| Feature | How it works |
|---|---|
| **🖐 Slide Control** | Open palm → Next slide, Peace sign → Previous slide |
| **🔊 Volume Control** | Pinch gesture (OK sign) — slide hand up/down to adjust volume |
| **🎵 Media Playback** | Custom gestures for play/pause, next/prev track |
| **📜 Scroll** | Jedi scroll gesture — wave your hand to scroll pages |
| **🔍 Pinch-to-Zoom** | Two-handed pinch — spread/squeeze to zoom in/out |
| **🎙 Voice Commands** | **Fist** → Silent Command Mode, **AI Mic** → User-defined mode (Command vs Assistant) |
| **🛡 Audience Proofing** | Face detection ensures only the presenter's hand is tracked |
| **⚙️ Custom Gestures** | Record your own hand shapes via the settings GUI |

---

## 🏗 Architecture

```
main.py                 ← Daemon entry point (system tray + camera loop)
├── gesture/
│   ├── detector.py     ← MediaPipe hand landmark detector
│   ├── classifier.py   ← Gesture classification (Euclidean distance matching)
│   ├── actions.py      ← OS-level actions (key presses, volume, media)
│   └── face_detector.py← Face detection for audience proofing
├── voice/
│   └── realtime_client.py ← OpenAI Realtime API voice assistant
├── settings.py         ← CustomTkinter configuration GUI
├── config.py           ← Camera & API configuration
└── custom_gestures.json← User-recorded gesture database
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A webcam
- Linux (tested on Kali Linux / Debian-based distros)
- PulseAudio (for volume control)
- `playerctl` (optional, for media control)

### Installation

```bash
# Clone the repository
git clone https://github.com/pirmakhmatov/aerocontrol.git
cd aerocontrol

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Additional system packages (Debian/Ubuntu)
sudo apt install portaudio19-dev python3-tk
```

### Configuration

```bash
# Copy the environment template and add your OpenAI API key
cp .env.template .env
nano .env   # paste your OPENAI_API_KEY
```

> **Note:** The voice assistant requires an OpenAI API key with Realtime API access. AeroControl works fully without it — voice commands will simply be disabled.

### Running

```bash
# Start the daemon
python main.py

# Open the settings GUI (also accessible from the tray icon)
python settings.py
```

AeroControl will:
1. Calibrate your hand size silently (hold your hand in front of the camera)
2. Appear as a green square icon in your system tray
3. Begin tracking gestures in the background

---

## ⚙️ Settings GUI

Launch from the system tray or run `python settings.py` directly.

- **Record custom gestures** — click any action, hold a hand shape in front of the camera
- **Toggle desktop notifications** — on/off + configurable duration
- **Enable debug window** — shows the live camera feed with hand landmarks
- **Clear all gestures** — reset the custom gesture database

---

## 🎙 Voice Commands

AeroControl features a dual-mode voice system powered by OpenAI's Realtime API:

1. **Silent Command Mode (✊ Fist)**: Best for quick, hands-free adjustments. The AI listens, executes the command silently (no speech back), and ignores conversational filler.
2. **AI Assistant Mode (🎙 Mic Gesture)**: A full conversational experience. The AI talks back to you, answers questions, and can still execute commands when mixed into conversation.

> [!TIP]
> You can change the behavior of the Mic gesture in the **Settings GUI** to switch between strict "Command Only" or "AI Assistant" modes.

### Whitelisted Commands
Regardless of mode, these commands are instantly matched and executed:

| Command | Action |
|---|---|
| "next slide" | Press → |
| "previous slide" / "go back" | Press ← |
| "volume up" / "louder" | Increase volume 20% |
| "volume down" / "quieter" | Decrease volume 20% |
| "set volume to 50" | Set absolute volume |
| "mute" / "unmute" | Toggle mute |
| "play" / "pause" | Toggle media playback |
| "next track" / "previous track" | Skip track |
| "full screen" / "start presentation" | Press F5 |
| "escape" / "exit" | Press Esc |

---

## 🧠 How Gesture Recognition Works

1. **Hand Detection** — MediaPipe extracts 21 hand landmarks per frame
2. **Calibration** — On startup, AeroControl measures your hand size for scale-invariant tracking
3. **Custom Gestures** — Matched via normalized Euclidean distance against saved templates
4. **Built-in Gestures** — Classified by finger curl/extension ratios relative to palm length
5. **Audience Proofing** — Face detection ensures gestures are only processed when the presenter is visible

---

## 📁 Requirements

```
opencv-python
mediapipe
pyautogui
pyaudio
websockets
python-dotenv
```

Additional Python packages installed automatically: `pystray`, `Pillow`, `customtkinter`, `numpy`.

---

## 📄 License

This project was built for the **April 2026 AI Hackathon** at the Qarshi Presidential School.

---

## 👤 Author

**Pirmakhmatov** — [@pirmakhmatov](https://github.com/pirmakhmatov)
