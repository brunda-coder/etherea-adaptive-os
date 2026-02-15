import { useEffect, useState } from 'react';

const TABS = ['Home', 'Workspace', 'Agent', 'Learn', 'Settings'] as const;

type Tab = (typeof TABS)[number];

export function TopBar({
  active,
  onTab,
  onSubmit,
}: {
  active: Tab;
  onTab: (tab: Tab) => void;
  onSubmit: (text: string) => void;
}) {
  const [online, setOnline] = useState(navigator.onLine);
  const [clock, setClock] = useState(new Date());
  const [text, setText] = useState('');

  useEffect(() => {
    const goOnline = () => setOnline(true);
    const goOffline = () => setOnline(false);
    window.addEventListener('online', goOnline);
    window.addEventListener('offline', goOffline);
    const timer = window.setInterval(() => setClock(new Date()), 60_000);
    return () => {
      window.removeEventListener('online', goOnline);
      window.removeEventListener('offline', goOffline);
      window.clearInterval(timer);
    };
  }, []);

  return (
    <header className="topbar card">
      <div className="brand">◉ Etherea WebOS</div>
      <nav>
        {TABS.map((tab) => (
          <button key={tab} className={active === tab ? 'active' : ''} onClick={() => onTab(tab)}>
            {tab}
          </button>
        ))}
      </nav>
      <form
        className="commandbar"
        onSubmit={(event) => {
          event.preventDefault();
          if (!text.trim()) return;
          onSubmit(text);
          setText('');
        }}
      >
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Type command or ask naturally" />
        <button type="submit">Send</button>
      </form>
      <div className="status">{online ? 'Wi-Fi' : 'Offline'} · {clock.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
    </header>
  );
}

export type { Tab };
