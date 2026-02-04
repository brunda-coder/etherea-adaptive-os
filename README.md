# Etherea - AI Explainer Avatar

This project demonstrates a secure and engaging way to integrate Gemini with a React frontend using Firebase.

## Setup & Deployment

### 1. Firebase Project Setup

1.  **Create a Firebase Project:** Go to the [Firebase Console](https://console.firebase.google.com/) and create a new project.
2.  **Upgrade to Blaze Plan:** Cloud Functions (2nd gen) requires the "Blaze" (pay-as-you-go) plan. You get a generous free tier.
3.  **Enable APIs:** In the Google Cloud console for your project, enable the following APIs:
    *   Artifact Registry API
    *   Cloud Run API
    *   Cloud Build API
    *   Identity and Access Management (IAM) API

### 2. Local Environment Setup

1.  **Install Firebase CLI:**

    ```bash
    npm install -g firebase-tools
    ```

2.  **Login to Firebase:**

    ```bash
    firebase login
    ```

3.  **Initialize Firebase:** In your project root, run:

    ```bash
    firebase init
    ```

    *   Select "Hosting" and "Functions".
    *   Choose an existing project and select the project you created.
    *   **Functions:**
        *   Language: JavaScript
        *   Use ESLint: Yes
        *   Install dependencies: Yes
    *   **Hosting:**
        *   Public directory: `frontend/dist` (or `frontend/build` if you use Create React App)
        *   Configure as a single-page app: Yes
        *   Set up automatic builds and deploys with GitHub: No

4.  **Set Project ID:**

    *   Open the `.firebaserc` file and replace `<YOUR_FIREBASE_PROJECT_ID>` with your actual Firebase project ID.

5.  **Set Gemini API Key:**

    *   Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   Set the API key as a secret in your Firebase project. Replace `<YOUR_GEMINI_API_KEY>` with your key.

    ```bash
    firebase functions:secrets:set GEMINI_API_KEY
    ```

    When prompted, enter your API key. This will store it securely in Secret Manager.

### 3. Run Locally with Emulators

1.  **Start Emulators:**

    ```bash
    firebase emulators:start
    ```

2.  **Access Local App:**

    *   The frontend will be available at `http://localhost:5000`.
    *   The functions will be available at `http://localhost:5001`.

### 4. Deploy to Production

1.  **Build Frontend:**

    ```bash
    cd frontend
    npm install
    npm run build
    cd ..
    ```

2.  **Deploy:**

    ```bash
    firebase deploy
    ```

## Project Structure

```
/
├── frontend/         # React (Vite) frontend application
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
├── functions/        # Firebase Functions (Node.js)
│   ├── index.js
│   ├── package.json
│   └── ...
├── firebase.json       # Firebase configuration
├── .firebaserc         # Firebase project configuration
└── README.md           # This file
```
