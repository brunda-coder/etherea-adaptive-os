# Firebase Hosting

Secrets for GitHub Actions:
- `FIREBASE_SERVICE_ACCOUNT`
- `FIREBASE_PROJECT_ID`

Local deploy:

```bash
cd etherea-webos/apps/web
npm install --prefix ../../
npm run build --prefix ../../ -w @etherea/web
firebase login
firebase use YOUR_FIREBASE_PROJECT_ID
firebase deploy --only hosting
```
