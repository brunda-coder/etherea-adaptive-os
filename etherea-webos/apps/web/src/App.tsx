import { useEffect, useMemo, useState } from 'react';
import { AgentPanel, type Message } from './components/AgentPanel';
import { AvatarStage, type Emotion } from './components/AvatarStage';
import { SettingsPanel } from './components/SettingsPanel';
import { TopBar, TABS, type Tab } from './components/TopBar';
import { Toast } from './components/Toast';
import { WorkspacePanel } from './components/WorkspacePanel';
import { executeCommand } from './lib/commands';
import { speak } from './lib/brain';
import { getVoiceState, speakReply, startListening, stopListening, stopSpeaking } from './lib/voice';
import { applyTheme, defaultTheme, loadTheme, saveTheme, type ThemeSettings } from './lib/theme';
import { listWorkspace, type WorkspaceFile } from './lib/workspaceStore';

const intro = 'Hey. I am Etherea. Want a quick EI demo? Ask: teach regression.';

type ToastState = { type: 'success' | 'error' | 'info'; message: string } | null;

export function App() {
  const [tab, setTab] = useState<Tab>('Home');
  const [messages, setMessages] = useState<Message[]>([{ role: 'etherea', text: intro }]);
  const [theme, setTheme] = useState<ThemeSettings>(() => loadTheme());
  const [emotion, setEmotion] = useState<Emotion>({ mood: 'calm', intensity: 0.4 });
  const [toast, setToast] = useState<ToastState>(null);
  const [files, setFiles] = useState<WorkspaceFile[]>([]);
  const [voiceStatus, setVoiceStatus] = useState('Voice OFF');

  const refreshWorkspace = async () => setFiles(await listWorkspace());

  useEffect(() => {
    refreshWorkspace();
  }, []);

  useEffect(() => {
    applyTheme(theme);
    saveTheme(theme);
  }, [theme]);

  useEffect(() => {
    if (!toast) return;
    const id = setTimeout(() => setToast(null), 2600);
    return () => clearTimeout(id);
  }, [toast]);

  useEffect(() => {
    const state = getVoiceState();
    setVoiceStatus(`${theme.voiceOutputEnabled ? 'Voice ON' : 'Voice OFF'} · ${state.recognitionSupported ? 'Mic ready' : 'Mic n/a'}`);
  }, [theme.voiceOutputEnabled, theme.micOptIn]);

  useEffect(() => {
    if (theme.privacyKillSwitch) {
      stopListening();
      if (theme.micOptIn) setTheme((prev) => ({ ...prev, micOptIn: false }));
      setToast({ type: 'info', message: 'Privacy kill switch forced mic OFF.' });
    }
  }, [theme.privacyKillSwitch, theme.micOptIn]);

  const onSubmit = async (text: string) => {
    setMessages((prev) => [...prev, { role: 'user', text }]);
    const result = await speak(text);
    setEmotion(result.emotion_update);
    setMessages((prev) => [...prev, { role: 'etherea', text: result.response }]);

    if (theme.voiceOutputEnabled) {
      const tts = speakReply(result.response);
      if (!tts.ok) setToast({ type: 'error', message: tts.reason ?? 'Voice output unavailable.' });
    }

    if (!result.command) return;
    try {
      const note = await executeCommand(result.command, theme, setTheme);
      setMessages((prev) => [...prev, { role: 'system', text: `Action: ${note}` }]);
      setToast({ type: 'success', message: note });
      await refreshWorkspace();
    } catch (error) {
      const reason = error instanceof Error ? error.message : 'Command failed';
      setMessages((prev) => [...prev, { role: 'system', text: `Action failed: ${reason}` }]);
      setToast({ type: 'error', message: reason });
    }
  };

  const home = useMemo(
    () => (
      <div className="home-grid">
        <AvatarStage emotion={emotion} reducedMotion={theme.reducedMotion} />
        <div className="stack">
          <AgentPanel messages={messages} />
          <WorkspacePanel files={files} onRefresh={refreshWorkspace} compact />
        </div>
      </div>
    ),
    [emotion, files, messages, theme.reducedMotion],
  );

  return (
    <main className="app-shell">
      <TopBar onSubmit={onSubmit} voiceStatus={voiceStatus} />

      <div className="frame">
        <aside className="nav-rail card">
          {TABS.map((item) => (
            <button key={item} className={tab === item ? 'active' : ''} onClick={() => setTab(item)}>
              {item}
            </button>
          ))}
          <button
            onClick={() => {
              if (!theme.micOptIn || theme.privacyKillSwitch) {
                setToast({ type: 'info', message: 'Mic is OFF by default. Enable mic opt-in in Settings first.' });
                return;
              }
              const started = startListening(
                (spokenText) => onSubmit(spokenText),
                (message) => setToast({ type: 'error', message }),
              );
              if (!started.ok) setToast({ type: 'error', message: started.reason ?? 'Mic unavailable.' });
            }}
          >
            Start Mic
          </button>
          <button onClick={() => stopListening()}>Stop Mic</button>
          <button onClick={() => stopSpeaking()}>Mute Voice</button>
        </aside>

        <section className="content">
          {tab === 'Home' && home}
          {tab === 'Workspace' && <WorkspacePanel files={files} onRefresh={refreshWorkspace} />}
          {tab === 'Agent' && <AgentPanel messages={messages} />}
          {tab === 'Learn' && <AgentPanel messages={[...messages, { role: 'etherea', text: 'Say “teach regression” or “what is emotional intelligence”.' }]} />}
          {tab === 'Settings' && <SettingsPanel theme={theme ?? defaultTheme} onTheme={setTheme} />}
        </section>
      </div>

      <nav className="bottom-nav card">
        {TABS.map((item) => (
          <button key={item} className={tab === item ? 'active' : ''} onClick={() => setTab(item)}>
            {item}
          </button>
        ))}
      </nav>

      <Toast message={toast?.message ?? null} type={toast?.type ?? 'info'} />
    </main>
  );
}
