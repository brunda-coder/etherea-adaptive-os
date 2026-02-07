# Release Artifacts

Create a release tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

`release.yml` uploads:
- Windows `.msi` + `.exe` from Tauri build
- Android `app-debug.apk` from Capacitor/Gradle build
- `web-dist.zip` from Vite output
