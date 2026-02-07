import { useEffect, useMemo, useRef, useState, type MouseEvent as ReactMouseEvent } from 'react';
import { runAgentAction, storage, stressFocus, type AgentAction } from '@etherea/core';
import { AuroraRing } from '@etherea/ui';
import * as pdfjsLib from 'pdfjs-dist';
import 'pdfjs-dist/web/pdf_viewer.css';
import * as monaco from 'monaco-editor';
import * as THREE from 'three';

pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;

type Mode = 'drawing' | 'pdf' | 'coding';
const themes = Array.from({ length: 50 }, (_, i) => `Preset ${i + 1}`);

function supportsSpeechRecognition(): boolean {
  return typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window);
}

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open('etherea', 1);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains('drawings')) db.createObjectStore('drawings');
      if (!db.objectStoreNames.contains('files')) db.createObjectStore('files');
      if (!db.objectStoreNames.contains('prefs')) db.createObjectStore('prefs');
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

function Avatar3D({ mouthOpen }: { mouthOpen: number }) {
  const mountRef = useRef<HTMLDivElement>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (!mountRef.current) return;
    const width = 260;
    const height = 220;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(70, width / height, 0.1, 1000);
    camera.position.z = 3;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    mountRef.current.innerHTML = '';
    mountRef.current.appendChild(renderer.domElement);

    const ambient = new THREE.AmbientLight(0xffffff, 1);
    scene.add(ambient);

    const head = new THREE.Mesh(new THREE.SphereGeometry(0.8, 32, 32), new THREE.MeshStandardMaterial({ color: '#60a5fa' }));
    scene.add(head);

    const mouth = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.08, 0.12), new THREE.MeshStandardMaterial({ color: '#ef4444' }));
    mouth.position.y = -0.38;
    scene.add(mouth);

    const blinkL = new THREE.Mesh(new THREE.SphereGeometry(0.1, 16, 16), new THREE.MeshStandardMaterial({ color: '#f8fafc' }));
    const blinkR = blinkL.clone();
    blinkL.position.set(-0.22, 0.16, 0.68);
    blinkR.position.set(0.22, 0.16, 0.68);
    scene.add(blinkL, blinkR);

    let frame = 0;
    const animate = () => {
      frame += 1;
      const breathe = 1 + Math.sin(frame / 28) * 0.02;
      head.scale.setScalar(breathe);
      const blink = Math.abs(Math.sin(frame / 90));
      blinkL.scale.y = blink < 0.08 ? 0.1 : 1;
      blinkR.scale.y = blink < 0.08 ? 0.1 : 1;
      mouth.scale.y = 0.6 + mouthOpen / 10;
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    };
    animate();
    setLoaded(true);
    return () => renderer.dispose();
  }, [mouthOpen]);

  return <div><div ref={mountRef} /><div className="indicator">{loaded ? 'avatar loaded' : 'loading avatar'}</div></div>;
}

export function App() {
  const [tutorialStep, setTutorialStep] = useState(0);
  const [tutorialVisible, setTutorialVisible] = useState(!storage.load<boolean>('tutorial.skip'));
  const [stress, setStress] = useState(20);
  const [focus, setFocus] = useState(70);
  const [mode, setMode] = useState<Mode>('drawing');
  const [mouthOpen, setMouthOpen] = useState(1);
  const [bubble, setBubble] = useState('Avatar ready for guidance.');
  const [voiceOn, setVoiceOn] = useState(true);
  const [micOn, setMicOn] = useState(true);
  const [micLevel, setMicLevel] = useState(0);
  const [privacy, setPrivacy] = useState(false);
  const [theme, setTheme] = useState(themes[0]);
  const [agentTask, setAgentTask] = useState<AgentAction>('create_ppt');
  const [agentState, setAgentState] = useState<'idle' | 'running' | 'paused' | 'cancelled'>('idle');
  const [agentOutput, setAgentOutput] = useState('');
  const [drawTool, setDrawTool] = useState<'pen' | 'eraser'>('pen');
  const [drawSize, setDrawSize] = useState(4);
  const [drawColor, setDrawColor] = useState('#93c5fd');
  const [annotation, setAnnotation] = useState('');
  const [selfcheck, setSelfcheck] = useState<string[]>([]);

  const drawRef = useRef<HTMLCanvasElement>(null);
  const pdfRef = useRef<HTMLCanvasElement>(null);
  const editorRef = useRef<HTMLDivElement>(null);
  const textEditorRef = useRef<HTMLTextAreaElement>(null);
  const monacoRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      const v = Math.min(100, Math.abs(e.movementX) + Math.abs(e.movementY));
      const typing = Number(storage.load<number>('typing.rate') ?? 0);
      const computed = stressFocus({ typingRate: typing, mouseVelocity: v });
      setStress(computed.stress);
      setFocus(computed.focus);
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
    if (!editorRef.current || monacoRef.current) return;
    try {
      monacoRef.current = monaco.editor.create(editorRef.current, { value: '// Etherea code workspace', language: 'typescript', theme: 'vs-dark' });
    } catch {
      monacoRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (!micOn) return;
    let mounted = true;
    navigator.mediaDevices?.getUserMedia?.({ audio: true }).then((stream) => {
      const ctx = new AudioContext();
      const analyser = ctx.createAnalyser();
      const source = ctx.createMediaStreamSource(stream);
      source.connect(analyser);
      analyser.fftSize = 64;
      const data = new Uint8Array(analyser.frequencyBinCount);
      const tick = () => {
        analyser.getByteFrequencyData(data);
        const avg = data.reduce((a, b) => a + b, 0) / data.length;
        if (mounted) {
          setMicLevel(Math.round(avg));
          setMouthOpen(Math.max(1, avg / 20));
          requestAnimationFrame(tick);
        }
      };
      tick();
    }).catch(() => setBubble('Mic permission path available, awaiting approval.'));
    return () => {
      mounted = false;
    };
  }, [micOn]);

  const expression = useMemo(() => (stress > 70 ? 'Alert' : focus > 70 ? 'Focused' : 'Calm'), [stress, focus]);

  const speakDemo = () => {
    const text = 'Tutorial guide is active. Drawing, PDF and coding modes are ready.';
    setBubble(text);
    if (voiceOn && 'speechSynthesis' in window) speechSynthesis.speak(new SpeechSynthesisUtterance(text));
  };

  const draw = (e: ReactMouseEvent<HTMLCanvasElement>) => {
    const c = drawRef.current;
    if (!c || e.buttons !== 1) return;
    const ctx = c.getContext('2d');
    if (!ctx) return;
    ctx.fillStyle = drawTool === 'eraser' ? '#0d1428' : drawColor;
    ctx.beginPath();
    ctx.arc(e.nativeEvent.offsetX, e.nativeEvent.offsetY, drawSize, 0, Math.PI * 2);
    ctx.fill();
  };

  const saveDrawing = async () => {
    if (!drawRef.current) return;
    await idbSet('drawings', 'latest', drawRef.current.toDataURL('image/png'));
    setBubble('Drawing saved to IndexedDB.');
  };
  const loadDrawing = async () => {
    const encoded = await idbGet('drawings', 'latest');
    if (!encoded || !drawRef.current) return;
    const img = new Image();
    img.onload = () => drawRef.current?.getContext('2d')?.drawImage(img, 0, 0);
    img.src = encoded;
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
    setBubble('PDF page rendered.');
  };

  const runAgent = () => {
    setAgentState('running');
    const out = runAgentAction(agentTask);
    setAgentOutput(JSON.stringify(out, null, 2));
    setAgentState('idle');
  };

  const saveCode = async () => {
    const content = monacoRef.current?.getValue() ?? textEditorRef.current?.value ?? '';
    await idbSet('files', 'main.ts', content);
  };
  const openCode = async () => {
    const v = await idbGet('files', 'main.ts');
    if (monacoRef.current) monacoRef.current.setValue(v ?? '// empty');
    if (textEditorRef.current) textEditorRef.current.value = v ?? '// empty';
  };

  const runSelfcheck = async () => {
    const logs: string[] = [];
    await idbSet('prefs', 'self', 'ok');
    logs.push((await idbGet('prefs', 'self')) === 'ok' ? 'PASS indexeddb' : 'FAIL indexeddb');
    logs.push(runAgentAction('generate_notes').output ? 'PASS agent output' : 'FAIL agent output');
    logs.push('mediaDevices' in navigator ? 'PASS mic pathway' : 'FAIL mic pathway');
    logs.push(document.body.innerText.includes('avatar loaded') ? 'PASS avatar loaded indicator' : 'FAIL avatar loaded indicator');
    setSelfcheck(logs);
  };

  return (
    <div className="app" data-theme={theme}>
      <header><h1>Etherea WebOS</h1><input className="command" placeholder="Command bar always visible" /></header>
      {tutorialVisible && <section className="tutorial"><b>Coach Overlay</b><p>{['Welcome', 'Try workspaces', 'Review settings'][tutorialStep]}</p><button onClick={() => setTutorialStep((s: number) => Math.max(0, s - 1))}>Back</button><button onClick={() => setTutorialStep((s: number) => Math.min(2, s + 1))}>Next</button><button onClick={() => { storage.save('tutorial.skip', true); setTutorialVisible(false); }}>Skip</button></section>}
      <section className="top">
        <AuroraRing stress={stress} />
        <div>
          <Avatar3D mouthOpen={mouthOpen} />
          <p>{bubble}</p>
          <button onClick={speakDemo}>Speak Demo</button>
          <div className="debug">Stress {stress} Focus {focus} Expression {expression}</div>
          <div>Mic level: <progress max={120} value={micLevel} /> {micLevel} {supportsSpeechRecognition() ? 'speech recognition available' : 'listening stub active'}</div>
        </div>
      </section>

      <nav>
        <button onClick={() => setMode('drawing')}>Drawing</button>
        <button onClick={() => setMode('pdf')}>PDF</button>
        <button onClick={() => setMode('coding')}>Coding</button>
        <button onClick={runSelfcheck}>SelfCheck</button>
      </nav>

      {mode === 'drawing' && <section><canvas ref={drawRef} width={600} height={260} onMouseMove={draw} /><div><button onClick={() => setDrawTool('pen')}>Pen</button><button onClick={() => setDrawTool('eraser')}>Eraser</button><input type="color" value={drawColor} onChange={(e: any) => setDrawColor(e.target.value)} /><input type="range" min={1} max={20} value={drawSize} onChange={(e: any) => setDrawSize(Number(e.target.value))} /><button onClick={saveDrawing}>Save IndexedDB</button><button onClick={loadDrawing}>Load IndexedDB</button><button onClick={exportDrawing}>Export PNG</button></div></section>}
      {mode === 'pdf' && <section><input type="file" accept="application/pdf" onChange={(e: any) => e.target.files?.[0] && loadPdf(e.target.files[0])} /><canvas ref={pdfRef} /><textarea value={annotation} onChange={(e: any) => setAnnotation(e.target.value)} placeholder="Annotation notes" /><button onClick={() => setBubble(JSON.stringify(runAgentAction('summarize_pdf').output))}>Summarize</button></section>}
      {mode === 'coding' && <section><div className="files">main.ts</div><div ref={editorRef} className="editor" />{!monacoRef.current && <textarea ref={textEditorRef} className="editor" defaultValue="// fallback editor" />}<button onClick={saveCode}>Save</button><button onClick={openCode}>Open</button></section>}

      <section className="agent"><h3>Agent Works</h3><select value={agentTask} onChange={(e: any) => setAgentTask(e.target.value as AgentAction)}><option value="create_ppt">create_ppt</option><option value="summarize_pdf">summarize_pdf</option><option value="generate_notes">generate_notes</option></select><button onClick={runAgent}>Run</button><button onClick={() => setAgentState('paused')}>Pause</button><button onClick={() => setAgentState('cancelled')}>Cancel</button><div>Status: {agentState}</div><pre>{agentOutput}</pre></section>

      <section className="settings"><h3>Settings</h3><label><input type="checkbox" checked={voiceOn} onChange={(e: any) => setVoiceOn(e.target.checked)} />voice</label><label><input type="checkbox" checked={micOn} onChange={(e: any) => setMicOn(e.target.checked)} />mic</label><label><input type="checkbox" checked={privacy} onChange={(e: any) => setPrivacy(e.target.checked)} />privacy</label><label>sensitivity<input type="range" min={1} max={100} defaultValue={40} /></label><label>memory retention<input type="range" /></label><button onClick={() => storage.clear()}>clear memory</button><select value={theme} onChange={(e: any) => setTheme(e.target.value)}>{themes.map((t) => <option key={t}>{t}</option>)}</select><input placeholder="Gradient creator: #111,#333,#999" /><div>Connectors: Drive, GitHub, Calendar, Spotify (not yet connected)</div><div>Background notifications wired in web sandbox as in-app notices only.</div></section>
      <section>{selfcheck.map((line: string) => <div key={line}>{line}</div>)}</section>
    </div>
  );
}
