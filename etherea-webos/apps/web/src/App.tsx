import { useEffect, useMemo, useRef, useState } from "react";
import * as pdfjsLib from "pdfjs-dist";
import { computeStressFocus, runAgentAction } from "@etherea/core";

(pdfjsLib as any).GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${(pdfjsLib as any).version}/build/pdf.worker.min.mjs`;

type Mode = "drawing" | "pdf" | "coding" | "agent" | "settings";

const themes = Array.from({ length: 50 }, (_, i) => `linear-gradient(120deg, hsl(${i * 7},80%,20%), hsl(${i * 7 + 60},80%,45%))`);

const dbPromise = new Promise<IDBDatabase>((resolve, reject) => {
  const req = indexedDB.open("etherea-db", 1);
  req.onupgradeneeded = () => req.result.createObjectStore("docs");
  req.onsuccess = () => resolve(req.result);
  req.onerror = () => reject(req.error);
});

async function dbSave(key: string, value: unknown) {
  const db = await dbPromise;
  const tx = db.transaction("docs", "readwrite");
  tx.objectStore("docs").put(value, key);
  await new Promise((resolve, reject) => {
    tx.oncomplete = () => resolve(null);
    tx.onerror = () => reject(tx.error);
  });
}
async function dbLoad<T>(key: string): Promise<T | null> {
  const db = await dbPromise;
  const tx = db.transaction("docs", "readonly");
  const req = tx.objectStore("docs").get(key);
  return await new Promise((resolve) => {
    req.onsuccess = () => resolve((req.result as T) ?? null);
    req.onerror = () => resolve(null);
  });
}

export function App() {
  const [mode, setMode] = useState<Mode>("drawing");
  const [showTutorial, setShowTutorial] = useState(localStorage.getItem("tutorialSkip") !== "true");
  const [typingCount, setTypingCount] = useState(0);
  const [mouseCount, setMouseCount] = useState(0);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [followCursor, setFollowCursor] = useState(true);
  const [wander, setWander] = useState(false);
  const [stress, setStress] = useState(0);
  const [focus, setFocus] = useState(100);
  const [bubble, setBubble] = useState("Ready.");
  const [agentTask, setAgentTask] = useState("Create exhibit keynote");
  const [agentOutput, setAgentOutput] = useState<any>(null);
  const [pdfSummary, setPdfSummary] = useState<any>(null);
  const [command, setCommand] = useState("");
  const [theme, setTheme] = useState(themes[0]);
  const avatarRef = useRef<HTMLCanvasElement>(null);
  const drawingRef = useRef<HTMLCanvasElement>(null);
  const codingRef = useRef<HTMLDivElement>(null);
  const [mouth, setMouth] = useState(6);

  useEffect(() => {
    const timer = setInterval(() => {
      const score = computeStressFocus({ typingPerMinute: typingCount * 6, mouseMovesPerMinute: mouseCount * 6 });
      setStress(score.stress);
      setFocus(score.focus);
      setTypingCount(0);
      setMouseCount(0);
    }, 10000);
    return () => clearInterval(timer);
  }, [typingCount, mouseCount]);

  useEffect(() => {
    const onMouse = () => setMouseCount((v) => v + 1);
    window.addEventListener("mousemove", onMouse);
    return () => window.removeEventListener("mousemove", onMouse);
  }, []);

  useEffect(() => {
    let x = 100;
    let y = 100;
    let tick = 0;
    const c = avatarRef.current;
    if (!c) return;
    const ctx = c.getContext("2d")!;
    let raf = 0;
    const draw = () => {
      tick += 0.05;
      ctx.clearRect(0, 0, c.width, c.height);
      const breathe = Math.sin(tick) * 3;
      const blink = Math.sin(tick * 2) > 0.96 ? 2 : 14;
      if (wander) {
        x = 100 + Math.sin(tick * 0.8) * 40;
        y = 100 + Math.cos(tick * 0.5) * 20;
      }
      ctx.fillStyle = "#d2defb";
      ctx.beginPath();
      ctx.arc(x, y + breathe, 44, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#0f1a34";
      ctx.fillRect(x - 18, y - 10 + breathe, 8, blink);
      ctx.fillRect(x + 10, y - 10 + breathe, 8, blink);
      ctx.fillRect(x - 12, y + 16 + breathe, 24, mouth);
      ctx.fillStyle = stress > 65 ? "#f84e4e" : "#62d5ff";
      ctx.beginPath();
      ctx.arc(x, y + 72, 18 + Math.sin(tick) * 3, 0, Math.PI * 2);
      ctx.fill();
      raf = requestAnimationFrame(draw);
    };
    draw();
    return () => cancelAnimationFrame(raf);
  }, [mouth, stress, wander]);

  useEffect(() => {
    let editor: any;
    import("monaco-editor").then((monaco) => {
      if (!codingRef.current) return;
      editor = monaco.editor.create(codingRef.current, {
        value: "// Etherea coding mode\nconsole.log('hello');",
        language: "typescript",
        automaticLayout: true,
        theme: "vs-dark"
      });
    });
    return () => editor?.dispose();
  }, []);

  const stressColor = stress > 65 ? "#ff3358" : "#53bbff";
  const expression = useMemo(() => (stress > 65 ? "Alert" : focus > 60 ? "Focused" : "Calm"), [stress, focus]);

  const speakDemo = () => {
    setBubble("Etherea is online. Adaptive workflow enabled.");
    if (voiceEnabled && "speechSynthesis" in window) {
      const utter = new SpeechSynthesisUtterance("Etherea is online. Adaptive workflow enabled.");
      utter.onboundary = () => setMouth(4 + Math.random() * 20);
      utter.onend = () => setMouth(6);
      speechSynthesis.speak(utter);
    } else {
      const t = setInterval(() => setMouth(4 + Math.random() * 20), 100);
      setTimeout(() => {
        clearInterval(t);
        setMouth(6);
      }, 1200);
    }
  };

  const runAgent = (action: "create_ppt" | "summarize_pdf" | "generate_notes") => {
    setAgentOutput(runAgentAction(action, agentTask, true));
  };

  const onPdf = async (file: File) => {
    const buf = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: buf }).promise;
    setBubble(`Loaded PDF: ${file.name} (${pdf.numPages} pages)`);
  };

  const saveDrawing = async () => {
    const data = drawingRef.current?.toDataURL("image/png") ?? "";
    await dbSave("drawing", data);
  };
  const exportDrawing = () => {
    const a = document.createElement("a");
    a.href = drawingRef.current?.toDataURL("image/png") ?? "";
    a.download = "drawing-export.png";
    a.click();
  };

  return (
    <div className="app" style={{ background: theme }} onKeyDown={() => setTypingCount((v) => v + 1)}>
      {!showTutorial && <div className="aurora" style={{ boxShadow: `0 0 24px 8px ${stressColor}` }} />}
      {showTutorial && (
        <div className="overlay">
          <h3>Tutorial</h3>
          <p>Boot ring, avatar, command bar, workspace modes.</p>
          <div><button onClick={() => setShowTutorial(false)}>Skip</button><button onClick={() => setShowTutorial(false)}>Next</button><button>Back</button></div>
          <label><input type="checkbox" onChange={() => localStorage.setItem("tutorialSkip", "true")} />persist skip</label>
        </div>
      )}

      <section className="topbar">
        {(["drawing", "pdf", "coding", "agent", "settings"] as Mode[]).map((m) => <button key={m} onClick={() => setMode(m)}>{m}</button>)}
        <div className="debug">stress {stress.toFixed(1)} | focus {focus.toFixed(1)}</div>
      </section>

      <section className="body">
        <aside>
          <canvas ref={avatarRef} width={240} height={240} />
          <p>{bubble}</p>
          <button onClick={speakDemo}>Speak Demo</button>
          <button onClick={() => setFollowCursor((v) => !v)}>follow cursor: {String(followCursor)}</button>
          <button onClick={() => setWander((v) => !v)}>wander: {String(wander)}</button>
          <p>Diagnostics: mode={wander ? "wander" : followCursor ? "follow" : "drag"} expression={expression} stress={stress.toFixed(1)}</p>
        </aside>
        <main>
          {mode === "drawing" && (
            <div>
              <h2>Drawing mode</h2>
              <canvas ref={drawingRef} width={720} height={320} className="draw" onMouseMove={(e) => {
                if (e.buttons !== 1) return;
                const ctx = drawingRef.current?.getContext("2d");
                if (!ctx) return;
                ctx.fillStyle = "#fff";
                ctx.beginPath();
                ctx.arc(e.nativeEvent.offsetX, e.nativeEvent.offsetY, 4, 0, Math.PI * 2);
                ctx.fill();
              }} />
              <button onClick={saveDrawing}>Save IndexedDB</button><button onClick={exportDrawing}>Export PNG</button><button onClick={async()=>{const d=await dbLoad<string>("drawing");if(d){const img=new Image();img.onload=()=>drawingRef.current?.getContext("2d")?.drawImage(img,0,0);img.src=d;}}}>Load IndexedDB</button>
            </div>
          )}
          {mode === "pdf" && (
            <div>
              <h2>PDF mode</h2>
              <input type="file" accept="application/pdf" onChange={(e) => e.target.files?.[0] && onPdf(e.target.files[0])} />
              <textarea placeholder="Annotations" rows={6} />
              <button onClick={() => setPdfSummary(runAgentAction("summarize_pdf", "Uploaded PDF", true).output)}>Summarize</button>
              <pre>{JSON.stringify(pdfSummary, null, 2)}</pre>
            </div>
          )}
          {mode === "coding" && (
            <div>
              <h2>Coding mode</h2>
              <p>Files: /index.ts, /README.md</p>
              <div ref={codingRef} className="editor" />
              <button onClick={async () => dbSave("code:index.ts", "console.log('saved')")}>Save IndexedDB</button>
              <button onClick={() => {
                const blob = new Blob(["console.log('export zip placeholder')"], { type: "text/plain" });
                const a = document.createElement("a");
                a.href = URL.createObjectURL(blob);
                a.download = "workspace.zip";
                a.click();
              }}>Export ZIP</button>
            </div>
          )}
          {mode === "agent" && (
            <div>
              <h2>Agent Works</h2>
              <input value={agentTask} onChange={(e) => setAgentTask(e.target.value)} />
              <button onClick={() => runAgent("create_ppt")}>create_ppt</button>
              <button onClick={() => runAgent("summarize_pdf")}>summarize_pdf</button>
              <button onClick={() => runAgent("generate_notes")}>generate_notes</button>
              <button>pause</button><button>cancel</button>
              <pre>{JSON.stringify(agentOutput, null, 2)}</pre>
            </div>
          )}
          {mode === "settings" && (
            <div>
              <h2>Settings</h2>
              <label><input type="checkbox" checked={voiceEnabled} onChange={(e) => setVoiceEnabled(e.target.checked)} />voice</label>
              <label><input type="checkbox" />mic</label>
              <label><input type="checkbox" />privacy mode</label>
              <label><input type="checkbox" defaultChecked />memory retention</label>
              <button onClick={async () => dbSave("memory", null)}>clear memory</button>
              <h3>Themes (50)</h3>
              <div className="themes">{themes.map((t) => <button key={t} style={{ background: t }} onClick={() => setTheme(t)} />)}</div>
              <h3>Gradient creator</h3>
              <p>Use theme presets then override with CSS in command bar.</p>
              <h3>Connectors (stubs)</h3>
              <p>Drive | GitHub | Calendar | Spotify</p>
              <input placeholder="Optional Gemini/OpenAI key" />
            </div>
          )}
        </main>
      </section>
      <footer><input value={command} onChange={(e) => setCommand(e.target.value)} placeholder="Command bar" /></footer>
    </div>
  );
}
