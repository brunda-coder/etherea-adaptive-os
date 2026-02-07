# Firebase Hosting (WebOS)

This repo deploys only `etherea-webos/apps/web/dist`.

## Required GitHub secrets
- `FIREBASE_PROJECT_ID`
- `FIREBASE_TOKEN`
- (legacy workflow) `FIREBASE_SERVICE_ACCOUNT_ETHEREA_WORKSPACE`

## Local smoke deploy
```bash
cd etherea-webos/apps/web
npm install --no-audit --no-fund
npm run build
npm run selfcheck
```
Then deploy from `etherea-webos` with your configured Firebase project.

## Workflow behavior
- Deploy workflows are path-filtered to WebOS/workflow changes.
- Web steps mirror CI: install, build, selfcheck from `etherea-webos/apps/web`.
- No desktop/android binaries are built in hosting deploy jobs.
