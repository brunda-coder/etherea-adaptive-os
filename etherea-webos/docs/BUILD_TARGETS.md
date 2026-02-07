# Manual build targets (not in CI)

CI intentionally avoids Android/Tauri builds due to restricted registry/system dependencies.

## Windows desktop (Tauri)
```bash
cd etherea-webos
npm ci
npm run build -w @etherea/web
cd apps/desktop-tauri
npm ci
npm run tauri build
```

## Android (Capacitor)
```bash
cd etherea-webos
npm ci
npm run build -w @etherea/web
cd apps/android-capacitor
npm ci
npm run sync
npx cap open android
```

These flows are scaffolding-ready and must be run on developer machines with SDKs installed.
