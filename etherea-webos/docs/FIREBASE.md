# Firebase Hosting Setup

## Required secrets (GitHub)
- `FIREBASE_SERVICE_ACCOUNT`
- `FIREBASE_PROJECT_ID`

## Local deploy commands
```bash
cd etherea-webos
npm install
npm run build -w @etherea/web
npx firebase-tools deploy --config apps/web/firebase.json --project <project-id>
```

Update `apps/web/.firebaserc` with your default project id placeholder.
