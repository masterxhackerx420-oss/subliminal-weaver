# 🐺 Subliminal Weaver

![WolfSec Subliminal Weaver](assets/logo.svg)

**WolfSec / DebianGang edition**

Open-source steganography tool for embedding and extracting messages in images and audio.  
Local-only. No telemetry. Built for creators, musicians, and researchers.

### Hosted Demo
**Try it live:** [https://huggingface.co/spaces/masterxhackerx420-oss/subliminal-weaver](https://huggingface.co/spaces/masterxhackerx420-oss/subliminal-weaver)

(If your Space name is different, replace the URL above.)

## Features

- LSB steganography for PNG / BMP images
- LSB steganography for WAV audio
- Optional password encryption (Fernet + PBKDF2)
- Basic analysis: LSB plane visualization and simple transition score
- Capacity calculator
- Expanded Gradio web UI (dark theme, capacity, analysis, audio support)
- CLI

## Quick Start (local)

```bash
git clone https://github.com/masterxhackerx420-oss/subliminal-weaver
cd subliminal-weaver
pip install -r requirements.txt
python web_ui.py          # web UI
# or
python weaver.py --help   # CLI
```

## Hugging Face Spaces
The `app.py` in this repo is ready for Spaces. If you already created the Space, make sure these files are present:
- `app.py`
- `web_ui.py`
- `requirements.txt`
- entire `core/` folder

## Responsible Use

For creative projects, personal privacy, and research. Do not use to conceal illegal content.

## License

MIT
