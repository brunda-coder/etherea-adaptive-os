# Etherea WebOS Prototype

## One-command checks

```bash
cd etherea-webos
npm install
npm run build
npm run selfcheck
```

## Local run

```bash
npm run dev -w @etherea/web
```

## Packaging

- Windows: `npm run build -w @etherea/desktop-tauri`
- Android: `npm run sync -w @etherea/android-capacitor && npm run build:apk -w @etherea/android-capacitor`
