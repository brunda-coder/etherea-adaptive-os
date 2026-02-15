import { useEffect, useMemo, useState } from 'react';
import { AgentPanel, type Message } from './components/AgentPanel';
import { AvatarStage, type Emotion } from './components/AvatarStage';
import { SettingsPanel } from './components/SettingsPanel';
import { TopBar, type Tab } from './components/TopBar';
import { Toast } from './components/Toast';
import { WorkspacePanel } from './components/WorkspacePanel';
import { executeCommand } from './lib/commands';
import { speak } from './lib/brain';
import { applyTheme, defaultTheme, loadTheme, saveTheme, type ThemeSettings } from './lib/theme';
import { listWorkspace, type WorkspaceFile } from './lib/workspaceStore';

const intro = 'Hi, I am Etherea. Want a quick EI demo? Ask: teach regression.';

export function App() {
  const [tab, setTab] = useState<Tab>('Home');
  const [messages, setMessages] = useState<Message[]>([{ role: 'etherea', text: intro }]);
  const [theme, setTheme] = useState<ThemeSettings>(() => loadTheme());
  const [emotion, setEmotion] = useState<Emotion>({ mood: 'calm', intensity: 0.4 });
  const [toast, setToast] = useState<string | null>(null);
  const [files, setFiles] = useState<WorkspaceFile[]>([]);

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
    const id = setTimeout(() => setToast(null), 2200);
    return () => clearTimeout(id);
  }, [toast]);

  const onSubmit = async (text: string) => {
    setMessages((prev) => [...prev, { role: 'user', text }]);
    const result = await speak(text);
    setEmotion(result.emotion_update);
    setMessages((prev) => [...prev, { role: 'etherea', text: result.response }]);
    if (!result.command) return;
    try {
      const note = await executeCommand(result.command, theme, setTheme);
      setMessages((prev) => [...prev, { role: 'system', text: `Action: ${note}` }]);
      setToast(note);
      await refreshWorkspace();
    } catch (error) {
      const reason = error instanceof Error ? error.message : 'Command failed';
      setMessages((prev) => [...prev, { role: 'system', text: `Action failed: ${reason}` }]);
      setToast(reason);
    }
  };

  const home = useMemo(
    () => (
      <div className="grid-two">
        <AvatarStage emotion={emotion} reducedMotion={theme.reducedMotion} />
        <AgentPanel messages={messages} />
      </div>
    ),
    [emotion, messages, theme.reducedMotion],
  );

  return (
    <main className="app-shell">
      <TopBar active={tab} onTab={setTab} onSubmit={onSubmit} />
      {tab === 'Home' && home}
      {tab === 'Workspace' && <WorkspacePanel files={files} onRefresh={refreshWorkspace} />}
      {tab === 'Agent' && <AgentPanel messages={messages} />}
      {tab === 'Learn' && <AgentPanel messages={[...messages, { role: 'etherea', text: 'Say “teach regression” or “teach probability”.' }]} />}
      {tab === 'Settings' && <SettingsPanel theme={theme ?? defaultTheme} onTheme={setTheme} />}
      <Toast message={toast} />
    </main>
  );
}
