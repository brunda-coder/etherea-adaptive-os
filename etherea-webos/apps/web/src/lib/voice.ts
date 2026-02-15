export type VoiceState = {
  speechSupported: boolean;
  recognitionSupported: boolean;
  speaking: boolean;
  listening: boolean;
};

type RecognitionLike = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: any) => void) | null;
  onerror: ((event: Event) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
};

type SpeechRecognitionCtor = new () => RecognitionLike;

const browser = window as Window & {
  webkitSpeechRecognition?: SpeechRecognitionCtor;
  SpeechRecognition?: SpeechRecognitionCtor;
};

let recognition: RecognitionLike | null = null;

export function getVoiceState(): VoiceState {
  return {
    speechSupported: typeof window !== 'undefined' && 'speechSynthesis' in window,
    recognitionSupported: Boolean(browser.SpeechRecognition || browser.webkitSpeechRecognition),
    speaking: typeof window !== 'undefined' && window.speechSynthesis.speaking,
    listening: Boolean(recognition),
  };
}

function chooseVoice(): SpeechSynthesisVoice | null {
  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find((voice) => /en-US|hi-IN/i.test(voice.lang));
  return preferred ?? voices[0] ?? null;
}

export function stopSpeaking() {
  if ('speechSynthesis' in window) window.speechSynthesis.cancel();
}

export function speakReply(text: string): { ok: boolean; reason?: string } {
  if (!('speechSynthesis' in window)) {
    return { ok: false, reason: 'Speech synthesis is not supported here.' };
  }
  stopSpeaking();
  const utterance = new SpeechSynthesisUtterance(text);
  const voice = chooseVoice();
  if (voice) utterance.voice = voice;
  utterance.rate = 1;
  utterance.pitch = 1;
  window.speechSynthesis.speak(utterance);
  return { ok: true };
}

export function startListening(
  onFinalText: (text: string) => void,
  onError: (message: string) => void,
): { ok: boolean; reason?: string } {
  if (recognition) return { ok: true };
  const Ctor = browser.SpeechRecognition ?? browser.webkitSpeechRecognition;
  if (!Ctor) return { ok: false, reason: 'Speech recognition not supported here.' };

  const instance = new Ctor();
  instance.continuous = false;
  instance.interimResults = false;
  instance.lang = 'en-US';
  instance.onresult = (event) => {
    const transcript = event.results?.[0]?.[0]?.transcript?.trim();
    if (transcript) onFinalText(transcript);
  };
  instance.onerror = () => {
    onError('Mic input failed. You can continue typing.');
  };
  instance.onend = () => {
    recognition = null;
  };

  recognition = instance;
  instance.start();
  return { ok: true };
}

export function stopListening() {
  recognition?.stop();
  recognition = null;
}
