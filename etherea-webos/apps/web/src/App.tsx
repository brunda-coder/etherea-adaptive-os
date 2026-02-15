import { Component, useEffect, useMemo, useState, type ReactNode } from 'react';
import { runAgentAction, storage, stressFocus, type AgentAction } from '@etherea/core';
import { AuroraRing } from '@etherea/ui';
import { AvatarStage } from './components/AvatarStage';
import { runOfflineBrain } from './lib/offlineBrain';

type MicState = 'idle' | 'requesting' | 'listening' | 'blocked';
type Tone = 'success' | 'error';
type GradientPreset = 'nebula' | 'pearl' | 'sunset' | 'mint' | 'violet';

type ThemeTokens = {
  accent: string;
  gradient: GradientPreset;
  glow: number;
  rounded: number;
  reducedMotion: boolean;
};

const defaultTokens: ThemeTokens = {
  accent: '#67e8f9',
  gradient: 'nebula',
  glow: 0.58,
  rounded: 16,
  reducedMotion: false,
};

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open('etherea', 2);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains('prefs')) db.createObjectStore('prefs');
      if (!db.objectStoreNames.contains('memory')) db.createObjectStore('memory');
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function idbSet(store: string, key: string, value: string) {
  const db = await openDB();
  const tx = db.transaction(store, 'readwrite');
  tx.objectStore(store).put(value, key);
}

async function idbGet(store: string, key: string): Promise<string | null> {
  const db = await openDB();
  return new Promise((resolve) => {
    const req = db.transaction(store, 'readonly').objectStore(store).get(key);
    req.onsuccess = () => resolve((req.result as string) || null);
    req.onerror = () => resolve(null);
  });
}

function applyTheme(tokens: ThemeTokens) {
  document.body.style.setProperty('--accent', tokens.accent);
  document.body.style.setProperty('--radius', `${tokens.rounded}px`);
  document.body.style.setProperty('--glow', String(tokens.glow));
  document.body.dataset.gradient = tokens.gradient;
  document.body.dataset.reduceMotion = tokens.reducedMotion ? 'on' : 'off';
}

function AppContent() {
  const [prompt, setPrompt] = useState('speak demo');
  const [reply, setReply] = useState('Welcome back. Etherea is awake in offline mode.');
  const [emotion, setEmotion] = useState<'calm' | 'curious' | 'hype' | 'care' | 'focused' | 'stressed'>('calm');
  const [voiceOn, setVoiceOn] = useState(storage.load<boolean>('voice.on') ?? false);
  const [privacyOn, setPrivacyOn] = useState(storage.load<boolean>('privacy.kill') ?? true);
  const [micOn, setMicOn] = useState(storage.load<boolean>('mic.on') ?? false);
  const [micState, setMicState] = useState<MicState>('idle');
  const [agentTask, setAgentTask] = useState<AgentAction>('generate_notes');
  const [agentState, setAgentState] = useState('idle');
  const [toast, setToast] = useState<{ msg: string; tone: Tone } | null>(null);
  const [costumeSpinKey, setCostumeSpinKey] = useState(0);
  const [tokens, setTokens] = useState<ThemeTokens>(() => storage.load<ThemeTokens>('theme.tokens') ?? defaultTokens);

  const focusModel = useMemo(() => stressFocus({ typingRate: 24, mouseVelocity: micOn ? 32 : 9 }), [micOn]);

  useEffect(() => {
    applyTheme(tokens);
    storage.save('theme.tokens', tokens);
    storage.save('ui.reduced_motion', tokens.reducedMotion);
  }, [tokens]);

  useEffect(() => {
    storage.save('voice.on', voiceOn);
  }, [voiceOn]);

  useEffect(() => {
    storage.save('privacy.kill', privacyOn);
    if (privacyOn) {
      setMicOn(false);
      setMicState('idle');
    }
  }, [privacyOn]);

  useEffect(() => {
    storage.save('mic.on', micOn);
  }, [micOn]);

  useEffect(() => {
    let ignore = false;
    (async () => {
      const old = await idbGet('memory', 'lastReply');
      if (!ignore && old) setReply(old);
    })();
    return () => {
      ignore = true;
    };
  }, []);

  useEffect(() => {
    if (!micOn) {
      setMicState('idle');
      return;
    }
    if (!navigator.mediaDevices?.getUserMedia) {
      setMicState('blocked');
      return;
    }

    let live = true;
    (async () => {
      setMicState('requesting');
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
        if (!live) {
          stream.getTracks().forEach((track) => track.stop());
          return;
        }
        setMicState('listening');
        stream.getTracks().forEach((track) => track.stop());
      } catch {
        if (live) setMicState('blocked');
      }
    })();

    return () => {
      live = false;
    };
  }, [micOn]);

  async function speakDemo() {
    const out = runOfflineBrain(prompt);
    setReply(out.response);
    setEmotion(out.emotion_update);
    setCostumeSpinKey((v) => v + 1);
    await idbSet('memory', 'lastReply', out.response);

    if (voiceOn && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(out.response);
      utterance.rate = 1;
      window.speechSynthesis.speak(utterance);
    }
  }

  async function runAgent() {
    setAgentState('running');
    const result = await runAgentAction(agentTask);
    setAgentState('done');
    setToast({ msg: `Agent ${agentTask} finished.`, tone: 'success' });
    window.setTimeout(() => setToast(null), 1800);
  }

  return (
    <div className="app">
      <header className="card app-header">
        <div>
          <h1>Etherea Adaptive OS</h1>
          <p>Local-first companion with animated avatar, privacy controls, and offline brain.</p>
        </div>
        <div className="ring-wrap">
          <AuroraRing stress={Math.max(0, focusModel.stress)} />
        </div>
      </header>

      <section className="hero-grid">
        <article className="card stage-card">
          <AvatarStage
            emotion={emotion}
            speaking={voiceOn}
            reducedMotion={tokens.reducedMotion}
            costumeSpinKey={costumeSpinKey}
            glowIntensity={tokens.glow}
          />
          <p className="meta">Emotion: {emotion} · Stress {focusModel.stress} · Focus {focusModel.focus}</p>
        </article>

        <article className="card">
          <h2>Offline Brain Demo</h2>
          <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} rows={5} />
          <div className="row">
            <button className="primary" onClick={speakDemo}>Speak Demo</button>
            <button onClick={() => setPrompt('teach regression')}>Teach Regression</button>
            <button onClick={() => setPrompt('EI intro')}>EI Intro</button>
          </div>
          <pre className="reply">{reply}</pre>
        </article>
      </section>

      <section className="card">
        <h3>Command Agent</h3>
        <select value={agentTask} onChange={(event) => setAgentTask(event.target.value as AgentAction)}>
          <option value="create_ppt">create_ppt</option>
          <option value="summarize_pdf">summarize_pdf</option>
          <option value="generate_notes">generate_notes</option>
        </select>
        <button onClick={runAgent}>Run</button>
        <p>{agentState}</p>
      </section>

      <section className="card settings-grid">
        <h3>Privacy + Theme</h3>
        <label><input type="checkbox" checked={voiceOn} onChange={(event) => setVoiceOn(event.target.checked)} /> Voice output</label>
        <label><input type="checkbox" checked={privacyOn} onChange={(event) => setPrivacyOn(event.target.checked)} /> Privacy kill-switch (ON = sensors OFF)</label>
        <label>
          <input type="checkbox" checked={micOn} disabled={privacyOn} onChange={(event) => setMicOn(event.target.checked)} />
          Microphone opt-in ({micState})
        </label>
        <label>
          <input
            type="checkbox"
            checked={tokens.reducedMotion}
            onChange={(event) => setTokens((old) => ({ ...old, reducedMotion: event.target.checked }))}
          />
          Reduced motion
        </label>

        <label>
          Accent color
          <input type="color" value={tokens.accent} onChange={(event) => setTokens((old) => ({ ...old, accent: event.target.value }))} />
        </label>
        <label>
          Gradient preset
          <select value={tokens.gradient} onChange={(event) => setTokens((old) => ({ ...old, gradient: event.target.value as GradientPreset }))}>
            <option value="nebula">Nebula</option>
            <option value="pearl">Pearl</option>
            <option value="sunset">Sunset</option>
            <option value="mint">Mint</option>
            <option value="violet">Violet</option>
          </select>
        </label>
        <label>
          Glow intensity
          <input
            type="range"
            min="0.1"
            max="1"
            step="0.05"
            value={tokens.glow}
            onChange={(event) => setTokens((old) => ({ ...old, glow: Number(event.target.value) }))}
          />
        </label>
        <label>
          Roundedness
          <input
            type="range"
            min="8"
            max="28"
            step="1"
            value={tokens.rounded}
            onChange={(event) => setTokens((old) => ({ ...old, rounded: Number(event.target.value) }))}
          />
        </label>
      </section>

      {toast && <div className={`toast ${toast.tone}`}>{toast.msg}</div>}
    </div>
  );
}

class AppErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean }> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  override render() {
    if (this.state.hasError) {
      return (
        <div className="card error-card">
          <h2>Etherea is resetting the interface.</h2>
          <p>Refresh to continue. Local memory remains intact.</p>
        </div>
      );
    }
    return this.props.children;
  }
}

export function App() {
  return (
    <AppErrorBoundary>
      <AppContent />
    </AppErrorBoundary>
  );
}


export default App;
