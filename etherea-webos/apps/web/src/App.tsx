import { useEffect, useMemo, useRef, useState } from 'react';
import { runAgentAction, storage, stressFocus } from '@etherea/core';
import { AuroraRing, AvatarFace } from '@etherea/ui';
import * as pdfjsLib from 'pdfjs-dist';
import 'pdfjs-dist/web/pdf_viewer.css';
import * as monaco from 'monaco-editor';

pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;

type Mode = 'drawing' | 'pdf' | 'coding';
type MoveMode = 'drag' | 'follow' | 'wander';

const themes = Array.from({ length: 50 }, (_, i) => `Preset ${i + 1}`);

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open('etherea', 1);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains('drawings')) db.createObjectStore('drawings');
      if (!db.objectStoreNames.contains('files')) db.createObjectStore('files');
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

export function App() {
  const [tutorial, setTutorial] = useState(storage.load<boolean>('tutorial.skip') ? false : true);
  const [stress, setStress] = useState(20);
  const [focus, setFocus] = useState(70);
  const [mode, setMode] = useState<Mode>('drawing');
  const [moveMode, setMoveMode] = useState<MoveMode>('drag');
  const [mouthOpen, setMouthOpen] = useState(2);
  const [bubble, setBubble] = useState('Ready.');
  const [voiceOn, setVoiceOn] = useState(true);
  const [privacy, setPrivacy] = useState(false);
  const [theme, setTheme] = useState(themes[0]);
  const [agentTask, setAgentTask] = useState('create_ppt');
  const [agentOutput, setAgentOutput] = useState('');
  const drawRef = useRef<HTMLCanvasElement>(null);
  const pdfRef = useRef<HTMLCanvasElement>(null);
  const editorRef = useRef<HTMLDivElement>(null);
  const monacoRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      const v = Math.min(100, Math.abs(e.movementX) + Math.abs(e.movementY));
      const typing = Number(storage.load<number>('typing.rate') ?? 0);
      const s = stressFocus({ typingRate: typing, mouseVelocity: v });
      setStress(s.stress);
      setFocus(s.focus);
    };
    const onType = () => storage.save('typing.rate', Math.min(100, Number(storage.load<number>('typing.rate') ?? 0) + 2));
    window.addEventListener('mousemove', onMove);
    window.addEventListener('keydown', onType);
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('keydown', onType);
    };
  }, []);

  useEffect(() => {
    if (editorRef.current && !monacoRef.current) {
      monacoRef.current = monaco.editor.create(editorRef.current, { value: '// Etherea code workspace', language: 'typescript', theme: 'vs-dark' });
    }
  }, []);

  const expression = useMemo(() => (stress > 70 ? 'Alert' : focus > 70 ? 'Focused' : 'Calm'), [stress, focus]);

  const speakDemo = () => {
    const text = 'Etherea speaking demo with synthetic voice and lip sync.';
    setBubble(text);
    let t = 0;
    const timer = setInterval(() => {
      t += 1;
      setMouthOpen(2 + Math.abs(Math.sin(t / 2)) * 10);
      if (t > 22) {
        clearInterval(timer);
        setMouthOpen(2);
      }
    }, 90);
    if (voiceOn && 'speechSynthesis' in window) {
      speechSynthesis.speak(new SpeechSynthesisUtterance(text));
    }
  };

  const draw = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const c = drawRef.current;
    if (!c || e.buttons !== 1) return;
    const ctx = c.getContext('2d');
    if (!ctx) return;
    ctx.fillStyle = '#93c5fd';
    ctx.beginPath();
    ctx.arc(e.nativeEvent.offsetX, e.nativeEvent.offsetY, 4, 0, Math.PI * 2);
    ctx.fill();
  };

  const saveDrawing = async () => {
    if (!drawRef.current) return;
    await idbSet('drawings', 'latest', drawRef.current.toDataURL('image/png'));
    setBubble('Drawing saved to IndexedDB.');
  };

  const exportDrawing = () => {
    if (!drawRef.current) return;
    const a = document.createElement('a');
    a.href = drawRef.current.toDataURL('image/png');
    a.download = 'etherea-drawing.png';
    a.click();
  };

  const loadPdf = async (file: File) => {
    const data = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data }).promise;
    const page = await pdf.getPage(1);
    const vp = page.getViewport({ scale: 1.2 });
    const canvas = pdfRef.current;
    if (!canvas) return;
    canvas.height = vp.height;
    canvas.width = vp.width;
    await page.render({ canvasContext: canvas.getContext('2d')!, viewport: vp }).promise;
  };

  const summarizePdf = () => setBubble(JSON.stringify(runAgentAction('summarize_pdf').output));

  const saveCode = async () => {
    await idbSet('files', 'main.ts', monacoRef.current?.getValue() ?? '');
    setBubble('Code saved to IndexedDB.');
  };

  const openCode = async () => {
    const v = await idbGet('files', 'main.ts');
    monacoRef.current?.setValue(v ?? '// empty');
  };

  const exportZip = async () => {
    const blob = new Blob([monacoRef.current?.getValue() ?? ''], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'workspace.zip';
    a.click();
  };

  const runTask = () => {
    const out = runAgentAction(agentTask as 'create_ppt' | 'summarize_pdf' | 'generate_notes');
    setAgentOutput(JSON.stringify(out, null, 2));
  };

  return (
    <div className="app" data-theme={theme}>
      <header><h1>Etherea WebOS</h1><input className="command" placeholder="Command bar always visible" /></header>
      {tutorial && <section className="tutorial"><b>Tutorial</b><p>Use Next/Back/Skip coach marks.</p><button>Back</button><button>Next</button><button onClick={() => { storage.save('tutorial.skip', true); setTutorial(false); }}>Skip</button></section>}
      <section className="top">
        {!tutorial && <AuroraRing stress={stress} />}
        <div>
          <AvatarFace mouthOpen={mouthOpen} expression={expression} />
          <p>{bubble}</p>
          <button onClick={speakDemo}>Speak Demo</button>
          <button onClick={() => setMoveMode('follow')}>Follow</button>
          <button onClick={() => setMoveMode('wander')}>Wander</button>
          <div>Diagnostics: {moveMode} / {expression} / stress {stress}</div>
        </div>
        <div className="debug">Debug: stress {stress} focus {focus}</div>
      </section>
      <nav>
        <button onClick={() => setMode('drawing')}>Drawing</button>
        <button onClick={() => setMode('pdf')}>PDF</button>
        <button onClick={() => setMode('coding')}>Coding</button>
      </nav>
      {mode === 'drawing' && <section><canvas ref={drawRef} width={600} height={260} onMouseMove={draw} /><div><button onClick={saveDrawing}>Save IndexedDB</button><button onClick={exportDrawing}>Export PNG</button></div></section>}
      {mode === 'pdf' && <section><input type="file" accept="application/pdf" onChange={(e) => e.target.files?.[0] && loadPdf(e.target.files[0])} /><canvas ref={pdfRef} /><textarea defaultValue="Annotations" /><button onClick={summarizePdf}>Summarize</button></section>}
      {mode === 'coding' && <section><div className="files">main.ts</div><div ref={editorRef} className="editor" /><button onClick={saveCode}>Save</button><button onClick={openCode}>Open</button><button onClick={exportZip}>Export Zip</button></section>}
      <section className="agent"><h3>Agent Works</h3><select value={agentTask} onChange={(e) => setAgentTask(e.target.value)}><option value="create_ppt">create_ppt</option><option value="summarize_pdf">summarize_pdf</option><option value="generate_notes">generate_notes</option></select><button onClick={runTask}>Run</button><pre>{agentOutput}</pre><div>Task/plan/steps/output with pause/cancel placeholders.</div></section>
      <section className="settings"><h3>Settings</h3><label><input type="checkbox" checked={voiceOn} onChange={(e) => setVoiceOn(e.target.checked)} />voice</label><label><input type="checkbox" />mic</label><label><input type="checkbox" checked={privacy} onChange={(e) => setPrivacy(e.target.checked)} />privacy</label><label>memory retention<input type="range" /></label><button onClick={() => storage.clear()}>clear memory</button><select value={theme} onChange={(e) => setTheme(e.target.value)}>{themes.map((t) => <option key={t}>{t}</option>)}</select><input placeholder="Gradient creator: #111,#333" /><div>Connectors: Drive / GitHub / Calendar / Spotify (stubs)</div><textarea placeholder="Optional Gemini/OpenAI API key stored locally" onBlur={(e) => storage.save('api.key', e.target.value)} /></section>
    </div>
  );
}
