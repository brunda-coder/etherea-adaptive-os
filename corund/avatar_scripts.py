from __future__ import annotations

from typing import Dict, List


SCRIPTS: Dict[str, Dict[str, List[str]]] = {
    "success": {
        "en-IN": [
            "All set. That’s done and in place.",
            "Completed. Let me know what you want next.",
            "Done. You’re good to go.",
            "Finished. Ready for the next step.",
        ],
        "hi-IN": [
            "हो गया। सब ठीक से पूरा हुआ।",
            "काम पूरा हो गया। आगे क्या करें?",
        ],
        "kn-IN": [
            "ಆಯಿತು. ಕೆಲಸ ಸರಿಯಾಗಿ ಮುಗಿದಿದೆ.",
            "ಕೆಲಸ ಮುಗಿದಿದೆ. ಮುಂದೇನು ಮಾಡೋಣ?",
        ],
        "ta-IN": [
            "முடிந்தது. எல்லாம் சரியாக முடிந்தது.",
            "வேலை முடிந்தது. அடுத்தது என்ன?",
        ],
        "te-IN": [
            "సరిపోయింది. అన్నీ సక్రమంగా పూర్తయ్యాయి.",
            "పని పూర్తైంది. ఇక తదుపరి ఏది?",
        ],
    },
    "blocked": {
        "en-IN": [
            "An override is on, so I’m paused for now.",
            "I’m held by an override. Tell me when to resume.",
            "Overrides are active. I’m on hold.",
            "Paused by an override. I can continue when you say.",
        ],
        "hi-IN": [
            "ओवरराइड सक्रिय है, इसलिए अभी मैं रुकी हुई हूँ।",
            "ओवरराइड चालू है। आप कहें तो मैं फिर शुरू करूँ।",
        ],
        "kn-IN": [
            "ಓವರ್‌ರೈಡ್ ಸಕ್ರಿಯವಾಗಿದೆ. ಈಗ ನಾನು ತಡೆಯಲ್ಪಟ್ಟಿದ್ದೇನೆ.",
            "ಓವರ್‌ರೈಡ್ ಚಾಲುವಿದೆ. ನೀವು ಹೇಳಿದಾಗ ಮುಂದುವರಿಸುತ್ತೇನೆ.",
        ],
        "ta-IN": [
            "மீறல் செயல்பாட்டில் உள்ளது. இப்போது நான் நிறுத்தப்பட்டுள்ளேன்.",
            "மீறல் நடப்பில் உள்ளது. சொன்னால் தொடர்கிறேன்.",
        ],
        "te-IN": [
            "ఓవర్‌రైడ్ అమల్లో ఉంది. ఇప్పటికీ నేను ఆపివున్నాను.",
            "ఓవర్‌రైడ్ ఉంది. మీరు చెప్పినప్పుడు కొనసాగిస్తాను.",
        ],
    },
    "error": {
        "en-IN": [
            "I hit an error. I can retry or stay text-only.",
            "Something didn’t work. I’ll stay in text-only for now.",
            "That didn’t go through. I can retry when you want.",
            "There was an error. I’ll keep this in text-only for now.",
        ],
        "hi-IN": [
            "त्रुटि हुई। चाहें तो मैं फिर से कोशिश कर सकती हूँ।",
            "कुछ ठीक नहीं हुआ। आप चाहें तो मैं फिर प्रयास करूँ।",
        ],
        "kn-IN": [
            "ದೋಷವಾಗಿದೆ. ನಾನು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಬಹುದು.",
            "ಏನೋ ತಪ್ಪಾಯಿತು. ನೀವು ಹೇಳಿದಾಗ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸುತ್ತೇನೆ.",
        ],
        "ta-IN": [
            "பிழை ஏற்பட்டது. மீண்டும் முயற்சி செய்யலாம்.",
            "ஏதோ தவறு ஏற்பட்டது. சொல்லுங்கள், மீண்டும் முயற்சிக்கிறேன்.",
        ],
        "te-IN": [
            "లోపం వచ్చింది. మళ్లీ ప్రయత్నించగలను.",
            "ఏదో తప్పు జరిగింది. మీరు చెప్పినప్పుడు మళ్లీ ప్రయత్నిస్తాను.",
        ],
    },
    "guidance": {
        "en-IN": [
            "I need one more detail to continue.",
            "Tell me the next step you want.",
            "Give me a bit more detail and I’ll proceed.",
            "What would you like me to do next?",
        ],
        "hi-IN": [
            "आगे बढ़ने के लिए थोड़ा और विवरण चाहिए।",
            "कृपया अगला कदम बताइए।",
        ],
        "kn-IN": [
            "ಮುಂದುವರಿಸಲು ಸ್ವಲ್ಪ ಹೆಚ್ಚಿನ ವಿವರ ಬೇಕು.",
            "ಮುಂದಿನ ಹೆಜ್ಜೆ ಏನು?",
        ],
        "ta-IN": [
            "தொடர ஒரு சிறிய கூடுதல் தகவல் தேவை.",
            "அடுத்த படி என்ன என்பதை சொல்லுங்கள்.",
        ],
        "te-IN": [
            "తదుపరి కొనసాగడానికి ఇంకొంత వివరాలు కావాలి.",
            "తదుపరి దశ ఏది చెప్పండి.",
        ],
    },
    "empathy": {
        "en-IN": [
            "I’ll keep it calm and steady. We can slow down.",
            "I’m here. Let’s keep it light and steady.",
            "We can take this slowly. I’m with you.",
            "Let’s keep it gentle and manageable.",
        ],
        "hi-IN": [
            "मैं शांत रखती हूँ। हम धीरे चल सकते हैं।",
            "हम धीरे-धीरे चल सकते हैं। मैं यहीं हूँ।",
        ],
        "kn-IN": [
            "ನಾನು ಶಾಂತವಾಗಿಯೇ ಇರುತ್ತೇನೆ. ನಾವು ನಿಧಾನವಾಗಿ ಸಾಗಬಹುದು.",
            "ನಿಧಾನವಾಗಿ ಸಾಗೋಣ. ನಾನು ಇಲ್ಲಿ ಇದ್ದೇನೆ.",
        ],
        "ta-IN": [
            "நான் அமைதியாக வைத்திருக்கிறேன். மெதுவாக செல்லலாம்.",
            "மெதுவாகச் செல்வோம். நான் உடன் இருக்கிறேன்.",
        ],
        "te-IN": [
            "నేను నెమ్మదిగా ఉంచుతాను. మెల్లగా సాగుదాం.",
            "నెమ్మదిగా సాగుదాం. నేను మీతోనే ఉన్నాను.",
        ],
    },
    "celebration": {
        "en-IN": [
            "Nice momentum. Keep that focus going.",
            "Strong progress. I’m right here with you.",
            "Great pace. Keep it going.",
            "Solid progress. You’ve got this.",
        ],
        "hi-IN": [
            "अच्छी प्रगति है। ऐसे ही आगे बढ़ें।",
            "बहुत बढ़िया। इसी तरह जारी रखें।",
        ],
        "kn-IN": [
            "ಚೆನ್ನಾದ ಪ್ರಗತಿ. ಇವನ್ನು ಮುಂದುವರಿಸೋಣ.",
            "ಚೆನ್ನಾಗಿದೆ. ಇದೇ ರೀತಿ ಮುಂದುವರಿಸಿ.",
        ],
        "ta-IN": [
            "சிறந்த முன்னேற்றம். இதே நேரத்தை தொடருங்கள்.",
            "நல்ல முன்னேற்றம். இதேபோல் தொடருங்கள்.",
        ],
        "te-IN": [
            "మంచి పురోగతి. ఇలానే కొనసాగిద్దాం.",
            "చాలా బాగుంది. ఇలాగే కొనసాగించండి.",
        ],
    },
}


def get_script(category: str, language_code: str) -> List[str]:
    category_scripts = SCRIPTS.get(category, {})
    return category_scripts.get(language_code) or category_scripts.get("en-IN", [])
