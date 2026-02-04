const functions = require("firebase-functions");
const admin = require("firebase-admin");
const { GoogleAIFileManager, GoogleGenerativeAI } = require("@google-ai/generativelanguage");

admin.initializeApp();

const cors = require("cors")({ origin: true });

// Access the GEMINI_API_KEY secret
const geminiApiKey = functions.config().keys.gemini_api_key;
const genAI = new GoogleGenerativeAI(geminiApiKey);

exports.api = functions.https.onRequest(async (req, res) => {
  cors(req, res, async () => {
    if (req.method !== "POST") {
      return res.status(405).json({ error: "Method Not Allowed" });
    }

    // Optional: Firebase Authentication check
    // const idToken = req.headers.authorization?.split('Bearer ')[1];
    // if (!idToken) {
    //   return res.status(401).json({ error: 'Unauthorized' });
    // }
    // try {
    //   const decodedToken = await admin.auth().verifyIdToken(idToken);
    //   req.user = decodedToken;
    // } catch (error) {
    //   return res.status(401).json({ error: 'Unauthorized' });
    // }

    try {
      const { userText, uiContext, userState, prefs } = req.body;

      // Basic payload validation
      if (!userText || !uiContext) {
        return res.status(400).json({ error: "Missing required fields" });
      }

      const model = genAI.getGenerativeModel({
         model: process.env.GEMINI_MODEL || "gemini-1.5-flash",
         generationConfig: { responseMimeType: "application/json" },
         systemInstruction: `You are an AI assistant for the Etherea application. Your goal is to help users understand the UI by providing structured JSON data. The user will provide their input and the current UI context. You must return a JSON object that follows the specified schema. The 'targetId' in the 'actions' array MUST match one of the 'id's from the provided 'uiContext.elements' array. If you cannot find a suitable target, you MUST use the 'toast' action type. Do NOT invent new 'targetId's.`
        });

      const prompt = `User query: "${userText}"\nUI Context: ${JSON.stringify(uiContext)}\nUser State: ${JSON.stringify(userState)}\nPreferences: ${JSON.stringify(prefs)}`;

      const result = await model.generateContent(prompt);
      const response = await result.response;
      const text = await response.text();

      res.status(200).json(JSON.parse(text));
    } catch (error) {
      console.error("Error processing request:", error);
      res.status(500).json({ error: "Internal Server Error" });
    }
  });
});
