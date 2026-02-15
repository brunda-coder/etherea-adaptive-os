import { useEffect, useState } from 'react';

export const TABS = ['Home', 'Workspace', 'Agent', 'Learn', 'Settings'] as const;

export type Tab = (typeof TABS)[number];

function EthereaMark() {
  return (
    <svg viewBox="0 0 32 32" aria-hidden="true" className="brand-mark">
      <defs>
        <linearGradient id="eth-grad" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stopColor="#67e8f9" />
          <stop offset="100%" stopColor="var(--accent)" />
        </linearGradient>
      </defs>
      <circle cx="16" cy="16" r="14" fill="url(#eth-grad)" opacity="0.18" />
      <path d="M8 18c2-6 14-8 16 0" stroke="url(#eth-grad)" strokeWidth="2.6" fill="none" strokeLinecap="round" />
      <circle cx="12" cy="13" r="2" fill="url(#eth-grad)" />
      <circle cx="20" cy="13" r="2" fill="url(#eth-grad)" />
    </svg>
  );
}

export function TopBar({
  onSubmit,
  voiceStatus,
}: {
  onSubmit: (text: string) => void;
  voiceStatus: string;
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
      <div className="brand-wrap">
        <EthereaMark />
        <div>
          <div className="brand">Etherea</div>
          <small>Adaptive WebOS</small>
        </div>
      </div>
      <form
        className="commandbar"
        onSubmit={(event) => {
          event.preventDefault();
          if (!text.trim()) return;
          onSubmit(text);
          setText('');
        }}
      >
        <span className="cmd-icon" aria-hidden="true">
          ⌘
        </span>
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Type a command or ask naturally" />
        <button type="submit">Send</button>
      </form>
      <div className="status-chips">
        <span className="chip">{online ? 'Wi-Fi' : 'Offline'}</span>
        <span className="chip">{clock.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        <span className="chip">{voiceStatus}</span>
        <span className="chip">⚙</span>
      </div>
    </header>
  );
}
