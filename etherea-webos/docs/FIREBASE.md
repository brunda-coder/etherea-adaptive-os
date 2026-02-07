# Firebase Hosting (WebOS)

This repo deploys only `etherea-webos/apps/web/dist` to Firebase Hosting site `etherea-adaptive-os` at:

- https://etherea-adaptive-os.web.app

## Required GitHub secrets
- `FIREBASE_PROJECT_ID` (set to `etherea-adaptive-os`)
- `FIREBASE_SERVICE_ACCOUNT_ETHEREA_WORKSPACE` (service account JSON)

## Local smoke deploy
```bash
cd etherea-webos/apps/web
npm install --no-audit --no-fund
npm run build
npm run selfcheck
```
Then deploy from `etherea-webos` with your configured Firebase project.

## Workflow behavior
- Deploy workflow is path-filtered to WebOS/workflow changes on `main`.
- Zero-binary guard runs before Node install/build/deploy.
- Web steps mirror CI: install, build, selfcheck from `etherea-webos/apps/web`.
- No desktop/android binaries are built in hosting deploy jobs.
