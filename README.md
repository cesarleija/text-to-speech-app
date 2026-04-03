# 🎙 Kaori Voice Studio

A desktop Text-to-Speech application powered by **Microsoft Edge Neural Voices** via [`edge-tts`](https://github.com/rany2/edge-tts). Convert any text to natural-sounding speech and export it as an MP3 file.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

---

## Features

- 🌍 **24 neural voices** across 10 languages (English, Spanish, French, German, Japanese, and more)
- 🎛 **Real-time controls** for speed, pitch, and volume
- 🔊 **In-app audio preview** — preview either the sample text or your full input text before exporting
- 💾 **MP3 export** with a single click
- 🎨 **Two themes** — Pink (default) and Dark
- ↕️ **Resizable window** with draggable split between text and voice panels

---

## Requirements

- Python **3.10 or higher**
- `tkinter` (included with most Python distributions)
- An internet connection (edge-tts streams audio from Microsoft servers)

> **Windows users:** Python from [python.org](https://python.org) includes tkinter by default.  
> **Linux users:** You may need to install it separately:
> ```bash
> sudo apt install python3-tk   # Debian/Ubuntu
> sudo dnf install python3-tkinter  # Fedora
> ```

---

## Installation

### Option 1 — Install from GitHub (recommended)

```bash
pip install git+https://github.com/YOUR_USERNAME/text-to-speech-app.git
```

Then launch it from anywhere:

```bash
kaori-voice-studio
```

---

### Option 2 — Clone and run locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/text-to-speech-app.git
cd text-to-speech-app

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python -m kaori_voice_studio.app
```

---

### Option 3 — Install as a local package

```bash
git clone https://github.com/YOUR_USERNAME/text-to-speech-app.git
cd text-to-speech-app
pip install .
kaori-voice-studio
```

---

## Usage

1. Type or paste your text into the **Text** panel.
2. Select a voice from the **Voice & Preview** dropdown.
3. Adjust **Speed**, **Pitch**, and **Volume** sliders as needed.
4. Click **▶ Preview Text** to hear your text, or **▶ Play Preview** to test the selected voice with a sample sentence.
5. Click **⬇ Export MP3** to save the audio file.

---

## Project Structure

```
text-to-speech-app/
├── kaori_voice_studio/
│   ├── __init__.py
│   └── app.py          # Main application
├── pyproject.toml      # Package metadata & build config
├── requirements.txt    # Runtime dependencies
├── .gitignore
└── README.md
```

---

## License

MIT — see [LICENSE](LICENSE) for details.
