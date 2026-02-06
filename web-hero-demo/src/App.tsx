import { useMemo, useState } from 'react'

const sampleMemory = [
  '09:10 - Opened focus workspace',
  '09:14 - Summarized standup notes',
  '09:22 - Enabled privacy mode',
]

export function HeroDemo() {
  const [autonomy, setAutonomy] = useState(false)
  const [privacy, setPrivacy] = useState(true)
  const [focus, setFocus] = useState(false)
  const [showPalette, setShowPalette] = useState(false)
  const [showMemory, setShowMemory] = useState(true)
  const speaking = useMemo(() => (autonomy ? 'Scanning calm opportunities…' : 'Autonomy is paused. Waiting for your command.'), [autonomy])

  return (
    <main className="hero-root">
      <div className="aurora-ring" aria-hidden="true" />
      <header className="top-bar panel">
        <h1>Etherea Hero Demo</h1>
        <input aria-label="Aurora search" placeholder="Search goals, commands, memories…" />
      </header>

      <section className="layout">
        <article className="panel command-panel">
          <h2>Command Surface</h2>
          <p>"open aurora" · "set focus mode for 25 minutes" · "summarize my session"</p>
          <button onClick={() => setShowPalette((v) => !v)}>Toggle Command Palette</button>
        </article>

        <article className="panel avatar-bubble">
          <h2>Avatar Bubble</h2>
          <p>{speaking}</p>
          <div className="pulse" />
        </article>

        <article className="panel toggles">
          <h2>Control Toggles</h2>
          <label><input type="checkbox" checked={autonomy} onChange={() => setAutonomy((v) => !v)} /> Autonomy ON/OFF</label>
          <label><input type="checkbox" checked={privacy} onChange={() => setPrivacy((v) => !v)} /> Privacy mode</label>
          <label><input type="checkbox" checked={focus} onChange={() => setFocus((v) => !v)} /> Focus mode</label>
          <button onClick={() => setShowMemory((v) => !v)}>Session Memory</button>
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
