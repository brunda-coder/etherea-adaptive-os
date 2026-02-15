import { useEffect, useMemo, useState } from 'react';
import { AvatarStage, type Emotion } from './components/AvatarStage';
import { Toast } from './components/Toast';
import { executeCommand } from './lib/commands';
import { speak } from './lib/brain';
import { applyTheme, loadTheme, saveTheme, type ThemeSettings } from './lib/theme';
import { listWorkspace, type WorkspaceFile } from './lib/workspaceStore';
import { getVoiceState, speakReply, startListening, stopListening, stopSpeaking } from './lib/voice';
import { useToast } from './lib/toast';

const TABS = ['Home', 'Workspace', 'Agent', 'Learn', 'Settings'] as const;
type Tab = (typeof TABS)[number];
type Message = { role: 'user' | 'etherea' | 'system'; text: string };

const intro = 'Hey, I am Etherea. Ask for “teach regression” to test teach mode.';
const quickCommands = ['teach regression', 'ei intro', 'list files', 'voice output on'];

export function App() {
  const [tab, setTab] = useState<Tab>('Home');
  const [messages, setMessages] = useState<Message[]>([{ role: 'etherea', text: intro }]);
  const [theme, setTheme] = useState<ThemeSettings>(() => loadTheme());
  const [emotion, setEmotion] = useState<Emotion>({ mood: 'calm', intensity: 0.5 });
  const [files, setFiles] = useState<WorkspaceFile[]>([]);
  const [voiceStatus, setVoiceStatus] = useState('Voice OFF · Mic n/a');
  const [composer, setComposer] = useState('');
  const [query, setQuery] = useState('');
  const [learnTopic, setLearnTopic] = useState('regression');
  const [learnResult, setLearnResult] = useState('');
  const { toast, showError, showInfo, showSuccess } = useToast();

  const refreshWorkspace = async () => setFiles(await listWorkspace());

  useEffect(() => {
    refreshWorkspace();
  }, []);

  useEffect(() => {
    applyTheme(theme);
    saveTheme(theme);
  }, [theme]);

  useEffect(() => {
    const state = getVoiceState();
    const micState = theme.privacyKillSwitch ? 'Mic blocked' : theme.micOptIn ? 'Mic opt-in' : 'Mic off';
    setVoiceStatus(`${theme.voiceOutputEnabled ? 'Voice ON' : 'Voice OFF'} · ${state.recognitionSupported ? micState : 'Mic n/a'}`);
  }, [theme.micOptIn, theme.privacyKillSwitch, theme.voiceOutputEnabled]);

  useEffect(() => {
    if (theme.privacyKillSwitch) {
      stopListening();
      if (theme.micOptIn) setTheme((prev) => ({ ...prev, micOptIn: false }));
      showInfo('Privacy kill switch forced mic OFF.');
    }
  }, [theme.privacyKillSwitch, theme.micOptIn, showInfo]);

  const submitPrompt = async (input: string) => {
    const text = input.trim();
    if (!text) return;

    setMessages((prev) => [...prev, { role: 'user', text }]);
    setComposer('');

    const result = await speak(text);
    setEmotion(result.emotion_update);
    setMessages((prev) => [...prev, { role: 'etherea', text: result.response }]);

    if (theme.voiceOutputEnabled && !theme.privacyKillSwitch) {
      const tts = speakReply(result.response);
      if (!tts.ok) showError(tts.reason ?? 'Voice output unavailable.');
    }

    if (!result.command) return;
    try {
      const note = await executeCommand(result.command, theme, setTheme);
      setMessages((prev) => [...prev, { role: 'system', text: `Action: ${note}` }]);
      showSuccess(note);
      await refreshWorkspace();
    } catch (error) {
      const reason = error instanceof Error ? error.message : 'Command failed';
      setMessages((prev) => [...prev, { role: 'system', text: `Action failed: ${reason}` }]);
      showError(reason);
    }
  };

  const filteredFiles = useMemo(() => files.filter((file) => file.path.toLowerCase().includes(query.toLowerCase())), [files, query]);

  return (
    <main className="app-shell">
      <header className="app-bar">
        <div className="brand-block">
          <div className="brand-dot" aria-hidden="true" />
          <div>
            <p className="title">Etherea</p>
            <p className="subtitle">Adaptive WebOS · Offline first</p>
          </div>
        </div>
        <div className="bar-chips">
          <span className="chip">Offline brain</span>
          <span className="chip">{new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          <button className="chip icon-btn" onClick={() => setTab('Settings')}>
            ⚙ Settings
          </button>
        </div>
      </header>

      <div className="layout-grid">
        <aside className="nav-rail">
          {TABS.map((item) => (
            <button key={item} className={`nav-btn ${tab === item ? 'active' : ''}`} onClick={() => setTab(item)}>
              {item}
            </button>
          ))}
        </aside>

        <section className="main-content">
          {tab === 'Home' && (
            <div className="section-stack">
              <section className="panel hero-panel">
                <AvatarStage emotion={emotion} reducedMotion={theme.reducedMotion} />
                <div className="quick-row">
                  <button onClick={() => submitPrompt('ei intro')}>EI Demo</button>
                  <button onClick={() => submitPrompt('teach regression')}>Teach Regression</button>
                  <button onClick={() => submitPrompt('run selfcheck')}>Selfcheck</button>
                </div>
                <div className="chip-row">
                  <span className="chip">Offline brain</span>
                  <span className="chip">{theme.micOptIn ? 'Mic opt-in active' : 'Mic off by default'}</span>
                  <span className="chip">{voiceStatus}</span>
                </div>
              </section>
            </div>
          )}

          {tab === 'Workspace' && (
            <section className="panel workspace-panel">
              <h2>Workspace</h2>
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search files" />
              <div className="workspace-actions">
                <button onClick={() => submitPrompt('create file notes.md with # Notes')}>New file</button>
                <button onClick={() => submitPrompt('list files')}>Refresh list</button>
              </div>
              <div className="file-list">
                {filteredFiles.length === 0 && <p className="small">No files yet. Try “create file notes.md”.</p>}
                {filteredFiles.map((file) => (
                  <div key={file.path} className="file-item">
                    <strong>{file.type === 'folder' ? '📁' : '📄'} {file.path}</strong>
                    <span className="small">{new Date(file.updatedAt).toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {tab === 'Agent' && (
            <section className="panel agent-panel">
              <h2>Agent</h2>
              <div className="quick-row">
                {quickCommands.map((command) => (
                  <button key={command} className="chip" onClick={() => submitPrompt(command)}>
                    {command}
                  </button>
                ))}
              </div>
              <div className="chatlog">
                {messages.map((message, index) => (
                  <div key={`${message.role}-${index}`} className={`bubble ${message.role}`}>
                    {message.text}
                  </div>
                ))}
              </div>
            </section>
          )}

          {tab === 'Learn' && (
            <section className="panel learn-panel">
              <h2>Teach mode</h2>
              <p className="small">Get a structured explanation: definition, example, steps, questions, exercise.</p>
              <div className="learn-form">
                <input value={learnTopic} onChange={(event) => setLearnTopic(event.target.value)} placeholder="Topic" />
                <button
                  onClick={async () => {
                    const result = await speak(`teach ${learnTopic}`);
                    setLearnResult(result.response);
                    setEmotion(result.emotion_update);
                    setMessages((prev) => [...prev, { role: 'user', text: `teach ${learnTopic}` }, { role: 'etherea', text: result.response }]);
                  }}
                >
                  Teach me
                </button>
              </div>
              <article className="learn-output">{learnResult || 'No lesson yet.'}</article>
            </section>
          )}

          {tab === 'Settings' && (
            <section className="panel settings-panel">
              <h2>Settings</h2>
              <label>Voice output
                <input type="checkbox" checked={theme.voiceOutputEnabled} onChange={(event) => setTheme({ ...theme, voiceOutputEnabled: event.target.checked })} />
              </label>
              <label>Mic opt-in
                <input
                  type="checkbox"
                  checked={theme.micOptIn}
                  onChange={(event) => {
                    if (theme.privacyKillSwitch && event.target.checked) {
                      showInfo('Disable privacy kill switch first to allow mic opt-in.');
                      return;
                    }
                    setTheme({ ...theme, micOptIn: event.target.checked });
                  }}
                />
              </label>
              <label>Privacy kill switch
                <input type="checkbox" checked={theme.privacyKillSwitch} onChange={(event) => setTheme({ ...theme, privacyKillSwitch: event.target.checked, micOptIn: event.target.checked ? false : theme.micOptIn })} />
              </label>
              <label>Reduced motion
                <input type="checkbox" checked={theme.reducedMotion} onChange={(event) => setTheme({ ...theme, reducedMotion: event.target.checked })} />
              </label>
              <label>Accent
                <input value={theme.accent} onChange={(event) => setTheme({ ...theme, accent: event.target.value })} />
              </label>
              <label>Glow {theme.glow.toFixed(2)}
                <input type="range" min="0" max="1" step="0.05" value={theme.glow} onChange={(event) => setTheme({ ...theme, glow: Number(event.target.value) })} />
              </label>
              <label>Rounded {theme.rounded}px
                <input type="range" min="8" max="26" step="1" value={theme.rounded} onChange={(event) => setTheme({ ...theme, rounded: Number(event.target.value) })} />
              </label>
              <div className="quick-row">
                <button onClick={() => stopSpeaking()}>Stop voice</button>
                <button
                  onClick={() => {
                    if (!theme.micOptIn || theme.privacyKillSwitch) {
                      showInfo('Mic is OFF by default. Enable Mic opt-in first.');
                      return;
                    }
                    const started = startListening(
                      (spoken) => submitPrompt(spoken),
                      (message) => showError(message),
                    );
                    if (!started.ok) showError(started.reason ?? 'Mic unavailable.');
                    else showSuccess('Listening started.');
                  }}
                >
                  Start mic
                </button>
                <button onClick={() => stopListening()}>Stop mic</button>
              </div>
            </section>
          )}
        </section>
      </div>

      <form
        className="command-dock"
        onSubmit={(event) => {
          event.preventDefault();
          submitPrompt(composer);
        }}
      >
        <input value={composer} onChange={(event) => setComposer(event.target.value)} placeholder="Type command or ask naturally" />
        <button type="submit">Send</button>
      </form>

      <nav className="bottom-nav">
        {TABS.map((item) => (
          <button key={item} className={`nav-btn ${tab === item ? 'active' : ''}`} onClick={() => setTab(item)}>
            {item}
          </button>
        ))}
      </nav>

      <Toast message={toast?.message ?? null} type={toast?.type ?? 'info'} />
    </main>
  );
}
