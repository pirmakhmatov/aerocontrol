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
| **🎙 Voice Commands/Assistant** | **Fist** → Silent Command Mode, **AI Mic** → User-defined mode (Command vs Assistant) |
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
**Telegram** - [@pirmaxmatov](t.me/pirmaxmatov)
**Instagram** - [@pirmakhmatov_](https://www.instagram.com/pirmakhmatov_)
**TG Channel** - [@pirmaxmatovs](t.me/pirmaxmatovs)

---

<br>

<h1 align="center">📊 Loyiha Taqdimoti / Project Pitch</h1>

<p align="center"><em>Aprel 2026 — Qarshi Prezident Maktabi AI Hackathon</em></p>

---

## 🔴 1. Muammo

### Taqdimotchilar va foydalanuvchilar noqulay vaziyatda

Bugungi kunda millionlab insonlar har kuni **taqdimotlar**, **onlayn darslar**, **vebinar** va **uy media tizimlari** bilan ishlaydi. Ammo barchasi bir muammoga duch keladi:

> **Kompyuterni boshqarish uchun doim klaviatura yoki sichqonchaga qaytish kerak.**

Bu muammo quyidagi holatlarda yaqqol namoyon bo'ladi:

- 🎤 **Taqdimotchilar** — ma'ruza paytida mikrofon qo'lda, slaydni almashtirish uchun kompyuterga yurish kerak. Bu professional ko'rinishni buzadi.
- 👨‍🏫 **O'qituvchilar** — doskada turib, masofadan kompyuterni boshqara olmaydi. Doimiy oldinga-orqaga yurish vaqtni behuda sarflaydi.
- ♿ **Nogironligi bo'lgan insonlar** — qo'l yoki barmoqlarini to'liq ishlata olmaydigan foydalanuvchilar uchun sichqoncha va klaviatura jiddiy to'siqdir.
- 🎮 **Media iste'molchilar** — filmlarni ko'rib, musiqa eshitib yotganida ovoz balandligini o'zgartirish uchun o'rnidan turib kompyuterga borish noqulay.
- 🏥 **Tibbiyot sohasida** — jarrohlar va shifokorlar steril muhitda tuyub ekranlarni boshqara olmaydi.

### Mavjud yechimlar nima uchun yetarli emas?

| Mavjud vosita | Kamchilik |
|---|---|
| **Bluetooth pult** | Qo'shimcha qurilma sotib olish va zaradlash kerak, faqat taqdimot uchun |
| **Telefon ilovalari** | Telefon qo'ldan tushib ketishi mumkin, Wi-Fi kerak, kechikish bor |
| **Siri / Google Assistant** | Faqat tegishli ekotizimda ishlaydi, desktop boshqaruviga cheklangan |
| **Leap Motion** | Qimmat ($100+), maxsus apparat, faqat ma'lum dasturlar bilan ishlaydi |

> 💡 **Xulosa:** Oddiy veb-kamera orqali, hech qanday qo'shimcha qurilmasiz kompyuterni boshqaradigan **bepul, universal, ochiq kodli yechim mavjud emas edi.**

---

## 🌍 2. Qamrov — Bu muammodan qancha inson aziyat chekadi?

Bu muammo global miqyosda **milliardlab** insonlarni qamrab oladi:

| Guruh | Taxminiy son | Manba |
|---|---|---|
| 🎤 Kundalik taqdimot qiluvchilar (biznes, ta'lim) | **500 million+** | Microsoft / Google Workspace statistikasi |
| 👨‍🏫 Onlayn va oflayn o'qituvchilar | **70 million+** | UNESCO |
| ♿ Harakat cheklangan insonlar | **1.3 milliard** | Butunjahon Sog'liqni Saqlash Tashkiloti (WHO) |
| 🎵 Media iste'molchilari (musiqa, film) | **4+ milliard** | Internet foydalanuvchilari soni |
| 🏥 Tibbiyot xodimlari | **60+ million** | WHO |

> 📊 **Faqat taqdimotchilar va o'qituvchilarning o'zi 500 million+** insonni tashkil qiladi. Agar media foydalanuvchilarni qo'shsak, amalda **har bir kompyuter foydalanuvchisi** bu muammoni his qiladi.

### O'zbekiston miqyosida

- 🏫 **Prezident maktablari** — har bir o'qituvchi proyektordan foydalanadi
- 🎓 **Universitetlar** — onlayn ta'limda 200,000+ talaba
- 🖥 **IT sohasida** — demo va taqdimotlar doimiy ish jarayonining bir qismi

---

## ✅ 3. Yechim — AeroControl

<p align="center">
  <strong>✋ AeroControl — qo'l ishoralari va ovozli buyruqlar orqali kompyuterni masofadan boshqarish tizimi</strong>
</p>

AeroControl — bu faqat **oddiy veb-kamera** va **sun'iy intellekt** yordamida ishlaydigan bepul, ochiq kodli dastur. U orqa fonda (daemon) tinch ishlaydi va foydalanuvchining qo'l harakatlarini hamda ovozli buyruqlarini real vaqtda tanib, tizimni avtomatik boshqaradi.

### Qanday ishlaydi?

```
📷 Veb-kamera → 🤖 MediaPipe AI → ✋ Ishora aniqlash → ⚡ Harakat bajarish
                                   🎙 Ovoz → OpenAI → 🗣 Buyruq bajarish
```

### Asosiy imkoniyatlar

| Imkoniyat | Tushuntirish |
|---|---|
| 🖐 **Slayd boshqaruvi** | Kaft ochish → keyingi slayd, ✌️ → oldingi slayd |
| 🔊 **Ovoz balandligi** | OK belgisi (pinch) — qo'lni yuqoriga/pastga suring |
| 🎵 **Media boshqaruvi** | Play/pause, keyingi/oldingi trek |
| 📜 **Scroll** | Qo'l silkitish orqali sahifalarni aylantirish |
| 🔍 **Zoom** | Ikki qo'l bilan pinch — kattalashtirish/kichiklashtirish |
| 🎙 **Ovozli buyruqlar** | "Keyingi slayd", "ovozni 50 ga qo'y" — tabiiy tilda |
| 🤖 **AI assistent** | Savollarga javob beradi, suhbatlashadi |
| 🛡 **Tomoshabin himoyasi** | Faqat taqdimotchi yuzini aniqlasa ishlaydi |
| ⚙️ **Maxsus ishoralar** | O'z ishoralaringizni yozib oling va tayinlang |

### Texnologik stek

| Texnologiya | Vazifasi |
|---|---|
| **MediaPipe** | 21 nuqtali qo'l skeleti aniqlash |
| **OpenCV** | Kamera oqimi va kadr qayta ishlash |
| **OpenAI Realtime API** | Ovozni real vaqtda matn va buyruqqa aylantirish |
| **PyAutoGUI** | Klaviatura va sichqoncha harakatlarini simulyatsiya qilish |
| **PulseAudio** | Linux tizim ovozini boshqarish |
| **pystray** | Tizim tray (fon rejimi) integratsiyasi |

---

## 🔄 4. Alternativlar — Mavjud o'xshash loyihalar

Biz bu muammoga yechim izlashdan oldin mavjud yechimlarni chuqur o'rganib chiqdik:

### 4.1. Gesture Recognition dasturlari

| Loyiha | Tavsif | Kamchiliklari |
|---|---|---|
| **Leap Motion Controller** | Maxsus infra-qizil sensor orqali qo'l harakatlarini aniqlaydi | ❌ Qimmat ($100+), alohida qurilma kerak, faqat ma'lum dasturlar bilan ishlaydi |
| **Flutter Hand Tracking** | Mobil qurilmalarda qo'l aniqlash | ❌ Faqat mobil, desktop boshqaruviga mo'ljallanmagan |
| **Gestify (GitHub)** | Python + MediaPipe asosida oddiy ishoralar | ❌ Faqat 2-3 ta ishora, ovozli buyruqlar yo'q, face detection yo'q |
| **MotionInput (UCL)** | Universitet loyihasi, kamera orqali boshqaruv | ❌ Windows only, o'rnatish murakkab, hujjatlari yetarli emas |

### 4.2. Ovozli boshqaruv tizimlari

| Loyiha | Tavsif | Kamchiliklari |
|---|---|---|
| **Siri / Google Assistant** | Tizim darajasidagi ovozli yordamchi | ❌ Faqat o'z ekotizimida, Linux da ishlamaydi, taqdimot boshqaruviga cheklangan |
| **Talon Voice** | Dasturchilar uchun ovozli boshqaruv | ❌ Juda murakkab o'rnatish, faqat ilg'or foydalanuvchilar uchun |

### 4.3. Nima uchun bu muammoga hali to'liq yechim yo'q edi?

1. **Birlashtirilmagan** — mavjud yechimlar faqat ishoralar YOKI faqat ovoz bilan ishlaydi, ikkalasini birlashtirgan loyiha yo'q
2. **Maxsus qurilma talab qiladi** — ko'pchilik loyihalar qimmat sensorlarni talab qiladi
3. **Platformaga bog'liq** — aksariyat yechimlar faqat bitta OT da ishlaydi
4. **Murakkab o'rnatish** — oddiy foydalanuvchi uchun juda qiyin

---

## 🏆 5. AeroControlning farqli jihatlari

> **Nima uchun foydalanuvchilar boshqa loyihalarni emas, aynan AeroControlni tanlashi kerak?**

| Xususiyat | AeroControl | Leap Motion | Gestify | Talon Voice | Google Assistant |
|---|---|---|---|---|---|
| 💰 Bepul va ochiq kodli | ✅ | ❌ ($100+) | ✅ | ✅ | ❌ |
| 📷 Faqat veb-kamera kerak | ✅ | ❌ (maxsus sensor) | ✅ | ✅ | ❌ |
| ✋ Qo'l ishoralari | ✅ (10+ ishora) | ✅ | ⚠️ (2-3 ta) | ❌ | ❌ |
| 🎙 Ovozli buyruqlar | ✅ (AI bilan) | ❌ | ❌ | ✅ | ✅ |
| 🤖 AI suhbat rejimi | ✅ | ❌ | ❌ | ❌ | ⚠️ |
| ⚙️ Maxsus ishoralar yaratish | ✅ | ❌ | ❌ | ❌ | ❌ |
| 🛡 Tomoshabin himoyasi | ✅ | ❌ | ❌ | ❌ | ❌ |
| 🐧 Linux qo'llab-quvvatlash | ✅ | ⚠️ | ✅ | ✅ | ❌ |
| 🔍 Pinch-to-Zoom | ✅ | ✅ | ❌ | ❌ | ❌ |
| 📜 Scroll boshqaruvi | ✅ | ✅ | ❌ | ❌ | ❌ |
| 🔊 Ovoz balandligi (ishora) | ✅ | ⚠️ | ❌ | ❌ | ✅ |

### Asosiy ustunliklar:

1. **Birinchi "all-in-one" yechim** — ishoralar + ovoz + AI bir joyda
2. **Nol xarajat** — faqat veb-kamera, qo'shimcha hech narsa kerak emas
3. **Maxsus ishoralar** — foydalanuvchi o'zi ishoralarni o'rgatadi (ML orqali)
4. **Tomoshabin himoyasi** — taqdimot paytida boshqalar noto'g'ri harakatlarni qilsa ham, tizim faqat taqdimotchi buyruqlarini bajaradi

---

## 🌟 6. Qo'shimcha ustunliklar

### 🧠 Sun'iy intellekt bilan chuqur integratsiya

AeroControl oddiy ishora aniqlash dasturi emas — u **to'liq AI tizimi**:

- **Machina o'rganish** — Maxsus ishoralar Evklid masofasi orqali taqqoslanadi. Foydalanuvchi o'z ishoralaringizni bir marta ko'rsatsa, tizim ularni har doim taniydi.
- **OpenAI Realtime API** — Ovozli buyruqlar tabiiy tilda qayta ishlanadi. "Ovozni biroz ko'tar" yoki "set volume to 50" — ikkalasi ham ishlaydi.
- **Ikki rejimli ovoz tizimi** — ✊ Mushtdek = jim buyruq rejimi (tizim javob bermaydi, faqat bajaradi), 🎙 Mikrofon ishorasi = AI assistent rejimi (suhbatlashadi va bajaradi).

### 🔒 Xavfsizlik va maxfiylik

- Kamera **faqat ishora aniqlash uchun** ishlatiladi — hech qanday rasm yoki video serverga yuborilmaydi
- Barcha ishlov berish **lokal (mahalliy)** amalga oshiriladi
- Ovozli buyruqlar faqat foydalanuvchi **faol ravishda ishora ko'rsatganda** qayta ishlanadi

### 🖥 Linux uchun yaratilgan

Ko'pchilik raqobatchilar faqat Windows yoki macOS ni qo'llab-quvvatlaydi. AeroControl **Linux-first** yondashuvga ega:
- PulseAudio orqali tizim ovozini boshqarish
- `playerctl` orqali media boshqaruvi
- `xdotool` / `pyautogui` orqali klaviatura simulyatsiyasi
- System tray integratsiyasi (`pystray`)

### ⚡ Yengil va tezkor

- Fon rejimida (daemon) ishlaydi — foydalanuvchi his qilmaydi
- **Resurs sarfi minimal** — kamera kadrlarini qayta ishlash optimizatsiya qilingan
- Tizim tray orqali bir klikda pauza/davom/sozlamalar

---

## 💰 7. Monetizatsiya — Loyiha qanday tirik qoladi?

### 📌 Asosiy model: Freemium + Premium

| Daraja | Narx | Imkoniyatlar |
|---|---|---|
| **🆓 Free (Bepul)** | $0 | Asosiy ishoralar (slayd, ovoz balandligi), 3 ta maxsus ishora, face detection |
| **⭐ Pro** | $5/oy yoki $29/yil | Cheksiz maxsus ishoralar, AI va ovozli assistent, zoom, scroll, media boshqaruvi |
| **🏢 Education/Enterprise** | $99/yil (tashkilot uchun) | Markaziy boshqaruv paneli, bir nechta foydalanuvchi, brending |

### 📊 Qo'shimcha daromad manbalari

1. **API litsenziyalash** — Boshqa dasturchilar AeroControlning ishora aniqlash engine'ini o'z loyihalarida ishlatishi mumkin
2. **Hardware hamkorlik** — Veb-kamera ishlab chiqaruvchilar bilan bundling (Logitech, Razer)
3. **Ta'lim sektori** — Maktab va universitetlarga maxsus litsenziya
4. **White-label yechim** — Korporativ mijozlar uchun brendlangan versiya

### 💡 Dastlabki bosqichda

- GitHub da **ochiq kodli** sifatida tarqatib, foydalanuvchilar bazasini o'stirish
- **Donatsiyalar** (GitHub Sponsors, Buy Me a Coffee)
- Hackathon va tanlovlarda **grant** olish
- Jamoa a'zolari ko'ngilli sifatida ishlaydi, loyiha o'sishi bilan moliyalashtirish jalb qilinadi

---

## 📈 8. Statistika va yutuqlar

### 🏅 Loyiha hozirgi holati

| Ko'rsatkich | Qiymat |
|---|---|
| 📅 Ishlab chiqish boshlangan | Aprel 2026 |
| 🧑‍💻 Jamoa hajmi | 1 dasturchi |
| 📦 Umumiy kod hajmi | 1000+ qator Python |
| ✋ Qo'llab-quvvatlanadigan ishoralar | 10+ (built-in) + cheksiz (custom) |
| 🎙 Ovozli buyruqlar soni | 15+ whitelisted buyruq |
| 🤖 AI modeli | OpenAI GPT-4o Realtime |
| 📷 Kerakli qurilma | Faqat veb-kamera |
| 🐧 Platforma | Linux (Debian/Ubuntu/Kali) |

### 🎯 Sinov natijalari

- ✅ **Slayd boshqaruvi** — 95%+ aniqlik bilan ishlaydi
- ✅ **Ovoz balandligi** — yumshoq va real-vaqtli boshqaruv
- ✅ **Ovozli buyruqlar** — tabiiy tilda (o'zbek, ingliz, rus) buyruqlarni tushunadi
- ✅ **Tomoshabin himoyasi** — auditoriya harakatlari filtrlangan
- ✅ **Maxsus ishoralar** — foydalanuvchi tomonidan o'rgatilgan ishoralar muvaffaqiyatli taniladi

---

## 🚀 9. Kelajakdagi rejalar

### 📍 Yaqin kelajak (2026-yil 2-yarmi)

- [ ] **Windows va macOS** qo'llab-quvvatlash qo'shish
- [ ] **Mobile companion app** — telefondan sozlamalarni boshqarish
- [ ] **Ko'p foydalanuvchi rejimi** — har bir foydalanuvchining qo'lini alohida tanish
- [ ] **Ishora kutubxonasi** — tayyor ishoralar to'plamini yuklab olish imkoniyati

### 📍 O'rta muddatli rejalar (2027)

- [ ] **Browser extension** — YouTube, Google Slides ichida to'g'ridan-to'g'ri ishlash
- [ ] **Raspberry Pi versiyasi** — arzon, portativ qurilma sifatida
- [ ] **API ochish** — boshqa dasturchilar uchun SDK
- [ ] **Zoom/Google Meet integratsiyasi** — onlayn uchrashuvlarda ishorali boshqaruv

### 📍 Uzoq muddatli vizion

- [ ] **AR/VR boshqaruvi** — virtual haqiqatda qo'l ishoralari bilan navigatsiya
- [ ] **Butun tana harakatlarini aniqlash** — faqat qo'l emas, butun tana ishoralari
- [ ] **IoT integratsiyasi** — uy qurilmalarini (chiroq, konditsioner) ishoralar bilan boshqarish
- [ ] **O'z-o'zidan o'rganuvchi model** — foydalanuvchi ishoralarini avto-optimallashtirish

---

<p align="center">
  <strong>🏆 AeroControl — kelajak bugun boshlanadi!</strong><br>
  <em>Aprel 2026 AI Hackathon — Qarshi Prezident Maktabi</em>
</p>

---

> **⭐ Agar loyiha sizga yoqsa, GitHub'da star qo'yishni unutmang!**

```bash
git clone https://github.com/pirmakhmatov/aerocontrol.git
```
