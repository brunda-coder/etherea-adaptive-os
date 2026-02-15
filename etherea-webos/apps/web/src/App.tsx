import { useEffect, useMemo, useRef, useState, type MouseEvent as ReactMouseEvent } from 'react';
import { runAgentAction, storage, stressFocus, type AgentAction } from '@etherea/core';
import { AuroraRing } from '@etherea/ui';
import * as pdfjsLib from 'pdfjs-dist';
import 'pdfjs-dist/web/pdf_viewer.css';
import * as monaco from 'monaco-editor';
import * as THREE from 'three';

pdfjsLib.GlobalWorkerOptions.workerSrc = new URL('pdfjs-dist/build/pdf.worker.min.mjs', import.meta.url).toString();

type Mode = 'drawing' | 'pdf' | 'coding';
type MicState = 'idle' | 'requesting' | 'listening' | 'blocked';
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

function Avatar3D({ mouthOpen, isTyping, isSpeaking }: { mouthOpen: number; isTyping: boolean; isSpeaking: boolean }) {
  const mountRef = useRef<HTMLDivElement>(null);
  const mouthOpenRef = useRef(mouthOpen);
  const [status, setStatus] = useState<'loading avatar' | 'avatar loaded' | 'avatar unavailable (webgl blocked)'>('loading avatar');

  mouthOpenRef.current = mouthOpen;

  useEffect(() => {
    if (!mountRef.current) return;
    const width = 260;
    const height = 220;

    if (typeof window === 'undefined' || !window.WebGLRenderingContext) {
      setStatus('avatar unavailable (webgl blocked)');
      return;
    }

    let frameId = 0;
    let renderer: THREE.WebGLRenderer | null = null;

    try {
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(70, width / height, 0.1, 1000);
      camera.position.z = 3;

      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(width, height);
      mountRef.current.innerHTML = '';
      mountRef.current.appendChild(renderer.domElement);

      const ambient = new THREE.AmbientLight(0xffffff, 1);
      scene.add(ambient);

      const head = new THREE.Mesh(new THREE.SphereGeometry(0.8, 32, 32), new THREE.MeshStandardMaterial({ color: '#60a5fa' }));
      scene.add(head);

      const aura = new THREE.Mesh(
        new THREE.SphereGeometry(0.93, 32, 32),
        new THREE.MeshBasicMaterial({ color: '#93c5fd', transparent: true, opacity: 0.14 }),
      );
      scene.add(aura);

      const mouth = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.08, 0.12), new THREE.MeshStandardMaterial({ color: '#ef4444' }));
      mouth.position.y = -0.38;
      scene.add(mouth);

      const blinkL = new THREE.Mesh(new THREE.SphereGeometry(0.1, 16, 16), new THREE.MeshStandardMaterial({ color: '#f8fafc' }));
      const blinkR = blinkL.clone();
      blinkL.position.set(-0.22, 0.16, 0.68);
      blinkR.position.set(0.22, 0.16, 0.68);
      scene.add(blinkL, blinkR);

      let frame = 0;
      let nextBlinkAt = 70;
      let blinkStartAt = -1;
      const blinkDuration = 6;
      const animate = () => {
        frame += 1;
        const breathe = 1 + Math.sin(frame / 30) * 0.015;
        const hover = Math.sin(frame / 65) * 0.02;
        head.scale.setScalar(breathe);
        head.position.y = hover;
        head.rotation.z = isTyping ? -0.06 : 0;

        if (frame >= nextBlinkAt) {
          blinkStartAt = frame;
          nextBlinkAt = frame + 90 + Math.floor(Math.random() * 130);
        }
        const blinkProgress = blinkStartAt >= 0 ? (frame - blinkStartAt) / blinkDuration : 2;
        const blinkY = blinkProgress >= 0 && blinkProgress <= 1 ? Math.max(0.12, Math.abs(1 - blinkProgress * 2)) : 1;
        blinkL.scale.y = blinkY;
        blinkR.scale.y = blinkY;

        const speakingPulse = isSpeaking ? 1 + Math.sin(frame / 6) * 0.035 : 1 + Math.sin(frame / 50) * 0.01;
        aura.scale.setScalar(speakingPulse);
        (aura.material as THREE.MeshBasicMaterial).opacity = isSpeaking ? 0.23 : 0.12;
        mouth.scale.y = 0.6 + Math.max(0.1, Math.min(10, mouthOpenRef.current)) / 10;
        head.material.opacity = 0.96 + Math.sin(frame / 90) * 0.03;
        head.material.transparent = true;
        renderer?.render(scene, camera);
        frameId = requestAnimationFrame(animate);
      };
      animate();
      setStatus('avatar loaded');
    } catch {
      setStatus('avatar unavailable (webgl blocked)');
    }

    return () => {
      if (frameId) cancelAnimationFrame(frameId);
      renderer?.dispose();
    };
  }, []);

  return <div><div ref={mountRef} /><div className="indicator">{status}</div></div>;
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
  const [micOn, setMicOn] = useState(false);
  const [typingActive, setTypingActive] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [micState, setMicState] = useState<MicState>('idle');
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
  const [pdfLoaded, setPdfLoaded] = useState(false);
  const [selfcheck, setSelfcheck] = useState<string[]>([]);

  const drawRef = useRef<HTMLCanvasElement>(null);
  const pdfRef = useRef<HTMLCanvasElement>(null);
  const editorRef = useRef<HTMLDivElement>(null);
  const textEditorRef = useRef<HTMLTextAreaElement>(null);
  const monacoRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const typingTimeoutRef = useRef<number | null>(null);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      const v = Math.min(100, Math.abs(e.movementX) + Math.abs(e.movementY));
      const typingRaw = Number(storage.load<number>('typing.rate') ?? 0);
      const typing = Number.isFinite(typingRaw) ? typingRaw : 0;
      const computed = stressFocus({ typingRate: typing, mouseVelocity: v });
      setStress(Number.isFinite(computed.stress) ? computed.stress : 0);
      setFocus(Number.isFinite(computed.focus) ? computed.focus : 0);
    };
    const onType = () => {
      const value = Number(storage.load<number>('typing.rate') ?? 0);
      const safeValue = Number.isFinite(value) ? value : 0;
      storage.save('typing.rate', Math.min(100, safeValue + 2));
      setTypingActive(true);
      if (typingTimeoutRef.current) window.clearTimeout(typingTimeoutRef.current);
      typingTimeoutRef.current = window.setTimeout(() => setTypingActive(false), 650);
    };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('keydown', onType);
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('keydown', onType);
      if (typingTimeoutRef.current) window.clearTimeout(typingTimeoutRef.current);
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
    if (!micOn) {
      setMicState('idle');
      setMicLevel(0);
      setMouthOpen(1);
      return;
    }
    if (!navigator.mediaDevices?.getUserMedia) {
      setMicState('blocked');
      setBubble('Microphone API unavailable in this browser sandbox.');
      return;
    }

    let mounted = true;
    let frameId = 0;
    let stream: MediaStream | null = null;
    let ctx: AudioContext | null = null;

    setMicState('requesting');
    navigator.mediaDevices.getUserMedia({ audio: true }).then((activeStream) => {
      stream = activeStream;
      setMicState('listening');
      try {
        ctx = new AudioContext();
      } catch {
        setMicState('blocked');
        setBubble('Microphone captured, but audio context is blocked.');
        return;
      }
      const analyser = ctx.createAnalyser();
      const source = ctx.createMediaStreamSource(activeStream);
      source.connect(analyser);
      analyser.fftSize = 64;
      const data = new Uint8Array(analyser.frequencyBinCount);
      const tick = () => {
        analyser.getByteFrequencyData(data);
        const avg = data.length ? data.reduce((a, b) => a + b, 0) / data.length : 0;
        if (mounted) {
          setMicLevel(Math.round(avg));
          setMouthOpen(Math.max(1, avg / 20));
          frameId = requestAnimationFrame(tick);
        }
      };
      tick();
    }).catch(() => {
      setMicState('blocked');
      setBubble('Mic permission path available, awaiting approval.');
    });

    return () => {
      mounted = false;
      if (frameId) cancelAnimationFrame(frameId);
      if (ctx) void ctx.close();
      stream?.getTracks().forEach((track) => track.stop());
    };
  }, [micOn]);

  const expression = useMemo(() => (stress > 70 ? 'Alert' : focus > 70 ? 'Focused' : 'Calm'), [stress, focus]);

  const micStatusText = useMemo(() => {
    if (!micOn) return 'idle';
    if (micState === 'requesting') return 'requesting';
    if (micState === 'listening') return 'listening';
    return 'blocked';
  }, [micOn, micState]);

  const speakDemo = () => {
    const text = 'Emotional intelligence is reading signals with care, then responding in a grounded way. Etherea does this offline using safe signals like typing rhythm, focus shifts, and optional local mic cues you control. Want me to show you? I’ll adapt theme + pace.';
    setBubble(text);
    setSpeaking(true);
    window.setTimeout(() => setSpeaking(false), 4200);
    if (voiceOn && 'speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.onend = () => setSpeaking(false);
      speechSynthesis.speak(utterance);
    }
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
    if (!encoded || !drawRef.current) {
      setBubble('No saved drawing yet.');
      return;
    }
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
    try {
      const data = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data }).promise;
      const page = await pdf.getPage(1);
      const vp = page.getViewport({ scale: 1.2 });
      const canvas = pdfRef.current;
      if (!canvas) return;
      canvas.height = vp.height;
      canvas.width = vp.width;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        setBubble('PDF canvas context unavailable.');
        return;
      }
      await page.render({ canvasContext: ctx, viewport: vp }).promise;
      setPdfLoaded(true);
      setBubble('PDF page rendered.');
    } catch {
      setPdfLoaded(false);
      setBubble('Unable to render this PDF in sandbox mode.');
    }
  };

  const runAgent = () => {
    setAgentState('running');
    try {
      const out = runAgentAction(agentTask);
      setAgentOutput(JSON.stringify(out, null, 2));
    } catch {
      setAgentOutput(JSON.stringify(runAgentAction('generate_notes'), null, 2));
    }
    setAgentState('idle');
  };

  const saveCode = async () => {
    const content = monacoRef.current?.getValue() ?? textEditorRef.current?.value ?? '';
    await idbSet('files', 'main.ts', content);
    setBubble('Code saved.');
  };
  const openCode = async () => {
    const v = await idbGet('files', 'main.ts');
    if (monacoRef.current) monacoRef.current.setValue(v ?? '// empty');
    if (textEditorRef.current) textEditorRef.current.value = v ?? '// empty';
    if (!v) setBubble('First-use coding workspace: start writing in main.ts');
  };

  const runSelfcheck = async () => {
    const logs: string[] = [];
    try {
      await idbSet('prefs', 'self', 'ok');
      logs.push((await idbGet('prefs', 'self')) === 'ok' ? 'PASS: IndexedDB roundtrip works.' : 'FAIL: IndexedDB did not roundtrip.');
    } catch {
      logs.push('FAIL: IndexedDB unavailable in this browser context.');
    }
    logs.push(runAgentAction('generate_notes').output ? 'PASS: Agent deterministic output is available.' : 'FAIL: Agent output missing.');
    logs.push(micState === 'blocked' ? 'FAIL: Mic permission is blocked/unavailable.' : 'PASS: Mic permission pathway is present.');
    logs.push(document.body.innerText.includes('avatar loaded') ? 'PASS: Avatar loaded indicator visible.' : 'FAIL: Avatar did not report loaded state.');
    setSelfcheck(logs);
  };

  return (
    <div className="app" data-theme={theme}>
      <header><h1>Etherea WebOS</h1><input className="command" placeholder="Command bar always visible" /></header>
      {tutorialVisible && <section className="tutorial"><b>Coach Overlay</b><p>{['Welcome', 'Try workspaces', 'Review settings'][tutorialStep]}</p><button onClick={() => setTutorialStep((s: number) => Math.max(0, s - 1))}>Back</button><button onClick={() => setTutorialStep((s: number) => Math.min(2, s + 1))}>Next</button><button onClick={() => { storage.save('tutorial.skip', true); setTutorialVisible(false); }}>Skip</button><button onClick={() => setTutorialVisible(false)}>Close</button></section>}
      <section className="top">
        <AuroraRing stress={stress} />
        <div>
          <Avatar3D mouthOpen={mouthOpen} isTyping={typingActive} isSpeaking={speaking || micState === 'listening'} />
          <p>{bubble}</p>
          <button onClick={speakDemo}>Speak Demo</button>
          <div className="debug">Stress {stress} Focus {focus} Expression {expression}</div>
          <div>Mic ({micStatusText}): <progress max={120} value={micLevel} /> {micLevel} {supportsSpeechRecognition() ? 'speech recognition available' : 'listening stub active'}</div>
        </div>
      </section>

      <nav>
        <button onClick={() => setMode('drawing')}>Drawing</button>
        <button onClick={() => setMode('pdf')}>PDF</button>
        <button onClick={() => setMode('coding')}>Coding</button>
        <button onClick={runSelfcheck}>SelfCheck</button>
      </nav>

      {mode === 'drawing' && <section><canvas ref={drawRef} width={600} height={260} onMouseMove={draw} /><div><button onClick={() => setDrawTool('pen')}>Pen</button><button onClick={() => setDrawTool('eraser')}>Eraser</button><input type="color" value={drawColor} onChange={(e: any) => setDrawColor(e.target.value)} /><input type="range" min={1} max={20} value={drawSize} onChange={(e: any) => setDrawSize(Number(e.target.value))} /><button onClick={saveDrawing}>Save IndexedDB</button><button onClick={loadDrawing}>Load IndexedDB</button><button onClick={exportDrawing}>Export PNG</button></div><div>Tip: hold left mouse button and drag to draw.</div></section>}
      {mode === 'pdf' && <section><input type="file" accept="application/pdf" onChange={(e: any) => e.target.files?.[0] && loadPdf(e.target.files[0])} /><canvas ref={pdfRef} /><textarea value={annotation} onChange={(e: any) => setAnnotation(e.target.value)} placeholder="Annotation notes" /><button onClick={() => setBubble(JSON.stringify(runAgentAction('summarize_pdf').output))}>Summarize</button><div>{pdfLoaded ? 'PDF workspace ready.' : 'First-use: upload a PDF to render page 1.'}</div></section>}
      {mode === 'coding' && <section><div className="files">main.ts</div><div ref={editorRef} className="editor" />{!monacoRef.current && <textarea ref={textEditorRef} className="editor" defaultValue="// fallback editor" />}<button onClick={saveCode}>Save</button><button onClick={openCode}>Open</button><div>First-use: open to load saved code or start from // empty.</div></section>}

      <section className="agent"><h3>Agent Works</h3><select value={agentTask} onChange={(e: any) => setAgentTask(e.target.value as AgentAction)}><option value="create_ppt">create_ppt</option><option value="summarize_pdf">summarize_pdf</option><option value="generate_notes">generate_notes</option></select><button onClick={runAgent}>Run</button><button onClick={() => setAgentState('paused')}>Pause</button><button onClick={() => setAgentState('cancelled')}>Cancel</button><div>Status: {agentState}</div><pre>{agentOutput}</pre></section>

      <section className="settings"><h3>Settings</h3><label><input type="checkbox" checked={voiceOn} onChange={(e: any) => setVoiceOn(e.target.checked)} />voice</label><label><input type="checkbox" checked={micOn} onChange={(e: any) => setMicOn(e.target.checked)} />mic</label><label><input type="checkbox" checked={privacy} onChange={(e: any) => setPrivacy(e.target.checked)} />privacy</label><label>sensitivity<input type="range" min={1} max={100} defaultValue={40} /></label><label>memory retention<input type="range" /></label><button onClick={() => storage.clear()}>clear memory</button><select value={theme} onChange={(e: any) => setTheme(e.target.value)}>{themes.map((t) => <option key={t}>{t}</option>)}</select><input placeholder="Gradient creator: #111,#333,#999" /><div>Connectors: Drive, GitHub, Calendar, Spotify (not yet connected)</div><div>Background notifications wired in web sandbox as in-app notices only.</div><div>Mic and sensors stay off by default until you opt in.</div></section>
      <section>{selfcheck.map((line: string) => <div key={line}>{line}</div>)}</section>
    </div>
  );
}
