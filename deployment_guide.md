# Etherea v3.0 Multi-Platform Deployment Guide 🚀

To transform Etherea from a Python project into a "Direct Download" OS experience across Windows, macOS, Android, and iOS, follow these industry-standard packaging workflows.

## 🪟 Windows (.exe) - *Recommended*
The fastest way to create a Windows installer.
1.  **Tool**: [PyInstaller](https://pyinstaller.org/) or [Nuitka](https://nuitka.net/) (for better performance).
2.  **Command**:
    ```bash
    pip install pyinstaller
    pyinstaller --noconsole --onefile --icon=assets/icon.ico core/ui/main_window_v2.py
    ```
3.  **Installer**: Use [Inno Setup](https://jrsoftware.org/isinfo.php) to create a professional `.exe` setup wizard.

---

## 🍎 macOS (.app / .dmg)
1.  **Tool**: [Py2App](https://py2app.readthedocs.io/) or [Briefcase](https://beeware.org/).
2.  **Briefcase Workflow**:
    ```bash
    pip install briefcase
    briefcase create
    briefcase build
    briefcase package --format dmg
    ```

---

## 📱 Mobile (Android & iOS)
Since Etherea v3.0 is built on **PySide6 (Qt)**, you should use the official **Qt for Python** mobile deployment strategies or the **BeeWare** suite.

### Android (.apk / .aab)
1.  **Tool**: [Briefcase](https://beeware.org/) or [Kivy/Buildozer](https://buildozer.readthedocs.io/) (requires some UI adjustments).
2.  **Briefcase**:
    ```bash
    briefcase create android
    briefcase build android
    briefcase run android
    ```

### iOS (.ipa)
> [!IMPORTANT]
> Requires a Mac with Xcode.
1.  **Tool**: [Briefcase](https://beeware.org/).
2.  **Workflow**:
    ```bash
    briefcase create ios
    briefcase build ios
    ```

---

## 📦 Automated GitHub Releases (Great Company Standard)
To provide "Direct Download" links like a pro:
1. Create a `.github/workflows/deploy.yml` file.
2. Configure it to auto-run PyInstaller/Briefcase on Every `git tag`.
3. This will automatically upload `.exe`, `.dmg`, and `.apk` files to your **Github Releases** page.

## 🌐 Web Direct (WASM)
You can compile PySide6 to the web using **Qt for WebAssembly**.
- This allows a "Try in Browser" button that downloads the OS logic directly into the browser cache.
