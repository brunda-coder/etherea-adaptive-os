# Manual build targets (not in CI)

CI intentionally validates WebOS web + desktop Python checks only.

## Windows desktop (Tauri)
```bash
cd etherea-webos
npm install --no-audit --no-fund
npm run build -w @etherea/web
cd apps/desktop-tauri
npm install --no-audit --no-fund
npm run tauri build
```

## Android (Capacitor)
```bash
cd etherea-webos
npm install --no-audit --no-fund
npm run build -w @etherea/web
cd apps/android-capacitor
npm install --no-audit --no-fund
npm run sync
npx cap open android
```

Run these only on machines with required SDK/toolchains.
