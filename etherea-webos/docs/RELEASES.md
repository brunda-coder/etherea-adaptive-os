# GitHub Releases Artifacts

## Trigger
Publish a GitHub Release tag (or run workflow_dispatch) to execute `etherea-webos/.github/workflows/release.yml`.

## Outputs attached to Release
- `web-dist.zip`
- Windows `.msi` / `.exe` from Tauri build
- Android `.apk` from Capacitor/Gradle build

## Local build commands
```bash
cd etherea-webos
npm install
npm run build -w @etherea/web
npm install --prefix apps/desktop-tauri && npm run build --prefix apps/desktop-tauri
npm install --prefix apps/android-capacitor && npm run sync --prefix apps/android-capacitor && npm run build:apk --prefix apps/android-capacitor
```
