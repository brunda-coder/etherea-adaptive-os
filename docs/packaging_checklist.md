# Etherea Packaging Checklist & Dependency Map

## Python Dependencies (install from requirements)
- `requirements.txt`
- `requirements-core.txt`
- `requirements-desktop.txt`
- `requirements-ui.txt`
- Optional (auto-detected by PyInstaller): `numpy`, `pygame`, `pyaudio`, `pyttsx3`, `speech_recognition`, `pynput`

## Qt Runtime Plugins (bundle with PySide6)
Required to avoid missing-plugin crashes:
- `platforms` (`windows` on Win, `xcb` on Linux)
- `imageformats` (PNG/WebP)
- `styles`
- `iconengines`
- `platformthemes`
- `xcbglintegrations` (Linux)

## Assets (must ship in build)
**Core assets**
- `core/assets/audio/etherea_theme_a.wav`
- `core/assets/audio/etherea_theme_b.wav`
- `core/assets/audio/etherea_theme_c.wav`
- `core/assets/animations/splash_pulse.json`
- `core/assets/models/aurora_placeholder.gltf`
- `core/assets/models/aurora_placeholder.bin`

**UI assets**
- `assets/avatar/face_idle.webp`
- `assets/audio/ui_click.wav`
- `assets/audio/ui_success.wav`
- `assets/audio/ui_whoosh.wav`
- `assets/demo/demo_script_01.json`
- `corund/assets/avatar.png` (AppImage icon)

## Runtime Data Paths
- Logs: `$ETHEREA_DATA_DIR/logs/etherea.log` (falls back to OS data directory)
- SQLite DB: `$ETHEREA_DATA_DIR/etherea.db`

## Packaging Commands (quick reference)
**Windows**
```powershell
./scripts/build_windows.ps1 -Version X.Y.Z
```

**Linux**
```bash
./scripts/build_linux.sh X.Y.Z
```

## Smoke Test Expectations
- `--self-test` launches the UI briefly, validates Aurora ring, Avatar panel, Command palette, workspace switching.
- Writes `self_test_ok.txt` in `$ETHEREA_DATA_DIR`.
