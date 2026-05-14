# Naraka Tool

A Windows utility for **Naraka: Bladepoint** with three features:

- **Character Physics** — unlocks hidden physics-based character animations
- **QR Converter** — converts CN Photobooth share QR codes to Global-compatible ones
- **CN Proxy** — intercepts and patches the game's API response so converted QR codes are accepted in-game

> UI supports English and Vietnamese (EN / VI toggle).

---

> **Important:** enable the proxy **after** logging into the game. Enabling before login may cause authentication issues. Disable VPN / GearUp before enabling.

---

## Requirements

- Windows 10 / 11
- Python 3.11+

Install dependencies:

```bash
pip install -r requirements.txt
```

`requirements.txt`:
```
customtkinter
Pillow
opencv-python
numpy
qrcode[pil]
requests
mitmproxy
logging
ctypes
sys
pathlib
```

---

## Usage

```bash
python main.py
```

### QR Converter workflow
1. Get a CN Photobooth screenshot (the one with the QR code).
2. Click **Select & Convert** and pick the image(s).
3. Converted images appear in `converted/`.
4. Log into the game, **then** enable CN Proxy.
5. In-game, scan the converted QR — the proxy patches the API response on the fly.

### Character Physics workflow
1. Select your platform (Steam / Epic / VNG / Custom).
2. Click **Enable Physics** (or **Auto Scan** to find all installations automatically).

---

## Disclaimer

This tool is intended for personal use to work around regional restrictions. Use at your own risk. Not affiliated with 24 Entertainment or NetEase.