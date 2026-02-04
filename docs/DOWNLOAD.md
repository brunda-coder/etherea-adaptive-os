# Etherea Downloads

## GitHub Releases

Download the latest release assets from GitHub:

- Windows: `Etherea-<VERSION>-Windows.exe`
- Linux: `Etherea-<VERSION>-Linux.AppImage`

Latest release:
- https://github.com/<OWNER>/<REPO>/releases/latest

Versioned release:
- https://github.com/<OWNER>/<REPO>/releases/tag/vX.Y.Z

## Running the App

### Windows
1. Download `Etherea-<VERSION>-Windows.exe`
2. Run the file (SmartScreen warning: choose **More info → Run anyway** if prompted).

### Linux
1. Download `Etherea-<VERSION>-Linux.AppImage`
2. Make it executable:
   ```bash
   chmod +x Etherea-<VERSION>-Linux.AppImage
   ```
3. Run:
   ```bash
   ./Etherea-<VERSION>-Linux.AppImage
   ```

## Troubleshooting

- **SmartScreen warning (Windows):** click **More info** → **Run anyway**.
- **Permission denied (Linux):** ensure the AppImage is executable.
- **Headless test (CI/offscreen):** use `QT_QPA_PLATFORM=offscreen`.
