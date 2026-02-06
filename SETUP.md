# Etherea Setup

## 1) Windows (PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-desktop.txt
```

## 2) Linux
```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-desktop.txt
```

## 3) Dev tools (optional)
```bash
pip install -r requirements-dev.txt
```

## 4) Optional feature extras
Install only what you need:

```bash
pip install pygame
pip install pyttsx3 SpeechRecognition edge-tts
pip install opencv-python mediapipe
```

## 5) Sanity checks
```bash
python -m compileall .
python tools/etherea_doctor.py
```

## 6) Optional git hook install
```bash
python scripts/install_hooks.py install
```
Use `python scripts/install_hooks.py uninstall` to remove it.
