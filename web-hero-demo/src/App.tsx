import { useMemo, useState } from 'react'

type Mode = 'Drawing' | 'PDF/Office' | 'Coding'
const modes: Mode[] = ['Drawing', 'PDF/Office', 'Coding']

const sampleMemory = [
  '09:10 - Opened focus workspace',
  '09:14 - Summarized standup notes',
  '09:22 - Enabled privacy mode',
]

const connectors = ['Google Drive', 'GitHub', 'Calendar', 'Spotify', 'Google Photos (optional)']

export function HeroDemo() {
  const [autonomy, setAutonomy] = useState(false)
  const [privacy, setPrivacy] = useState(true)
  const [mode, setMode] = useState<Mode>('Drawing')
  const [showPalette, setShowPalette] = useState(false)
  const [showMemory, setShowMemory] = useState(true)
  const [lipSync, setLipSync] = useState(42)
  const speaking = useMemo(() => (autonomy ? 'Scanning calm opportunities…' : 'Autonomy is paused. Waiting for your command.'), [autonomy])

  return (
    <main className="hero-root">
      <div className="aurora-ring" aria-hidden="true" />
      <header className="top-bar panel">
        <h1>Etherea Hero Demo</h1>
        <input aria-label="Aurora search" placeholder='Voice command mock: "switch to coding mode"' />
      </header>

      <section className="layout">
        <article className="panel command-panel">
          <h2>Workspace Mode Switching</h2>
          <p>Primary path: voice command routing into mode manager.</p>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {modes.map((m) => <button key={m} onClick={() => setMode(m)}>{m}</button>)}
          </div>
          <p><strong>Current:</strong> {mode}</p>
          <button onClick={() => setShowPalette((v) => !v)}>Toggle Command Palette</button>
        </article>

        <article className="panel avatar-bubble">
          <h2>Avatar + Lip-sync meter</h2>
          <p>{speaking}</p>
          <div className="pulse" />
          <label>lip-sync amplitude: {lipSync}</label>
          <input type="range" min={0} max={100} value={lipSync} onChange={(e) => setLipSync(Number(e.target.value))} />
        </article>

        <article className="panel toggles">
          <h2>Settings + Themes</h2>
          <label><input type="checkbox" checked={autonomy} onChange={() => setAutonomy((v) => !v)} /> Agent autonomy</label>
          <label><input type="checkbox" checked={privacy} onChange={() => setPrivacy((v) => !v)} /> Privacy mode</label>
          <div style={{ height: 28, borderRadius: 8, background: 'linear-gradient(135deg, #6fe0ff, #8b5cf6, #fb7185)' }} />
          <small>Gradient theme creator preview.</small>
          <button onClick={() => setShowMemory((v) => !v)}>Session Memory</button>
        </article>
      </section>

      <section className="layout" style={{ marginTop: 12 }}>
        <article className="panel" style={{ width: '100%' }}>
          <h3>Connectors Mock Panel</h3>
          <ul>{connectors.map((c) => <li key={c}>{c}</li>)}</ul>
        </article>
      </section>

      {showMemory && (
        <aside className="panel memory-panel">
          <h3>Session Memory (mock)</h3>
          <ul>{sampleMemory.map((item) => <li key={item}>{item}</li>)}</ul>
          <small>Local-first retention visualization.</small>
        </aside>
      )}

      {showPalette && (
        <div className="palette-overlay" role="dialog" aria-label="Command palette">
          <div className="panel palette">
            <h3>Command Palette</h3>
            <input autoFocus placeholder="Type a natural-language command…" />
          </div>
        </div>
      )}
    </main>
  )
}
