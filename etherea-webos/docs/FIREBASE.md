# Firebase Hosting (WebOS)

This repository deploys only the WebOS app from `etherea-webos/apps/web/dist`.

## Required GitHub Secrets
- `FIREBASE_PROJECT_ID`
- `FIREBASE_TOKEN` (CI token from `firebase login:ci`)

## Local setup
```bash
cd etherea-webos
npm ci
npm run build
firebase login
firebase use <your-project-id>
firebase deploy --only hosting --project <your-project-id>
```

## Notes
- Deployment workflow runs only on `push` to `main`.
- No desktop/android binaries are built in CI.
