# Subliminal Weaver

**WolfSec / DebianGang edition**

Open-source steganography tool for embedding and extracting messages in images and audio.  
Local-only. No telemetry. Built for creators, musicians, and researchers.

## Features

- LSB steganography for PNG / BMP images
- LSB steganography for WAV audio
- Optional password encryption (Fernet / PBKDF2)
- Basic analysis: LSB plane visualization and simple transition score
- Capacity calculator
- Pure CLI and expanded Gradio web UI (dark theme, capacity, analysis, audio support)

## Install

```bash
cd subliminal_weaver
pip install -r requirements.txt
```

## Usage

### CLI
```bash
python weaver.py embed cover.png "The cache is the ghost" -o secret.png
python weaver.py extract secret.png
python weaver.py embed track.wav "Red Rocket Howl" -o hidden.wav -p mysecret
```

### Web UI
```bash
python web_ui.py
```

## Responsible Use

For creative projects, personal privacy, and research. Do not use to conceal illegal content.

## License

MIT
