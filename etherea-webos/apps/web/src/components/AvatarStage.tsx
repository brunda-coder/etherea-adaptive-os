import { useEffect, useMemo, useState } from 'react';

export type Emotion = { mood: 'calm' | 'focused' | 'curious' | 'hype' | 'care' | 'stressed'; intensity: number };

export function AvatarStage({ emotion, reducedMotion }: { emotion: Emotion; reducedMotion: boolean }) {
  const [blink, setBlink] = useState(false);
  const [glance, setGlance] = useState(-2);

  useEffect(() => {
    if (reducedMotion) return;
    let alive = true;
    const tick = () => {
      const wait = 3000 + Math.random() * 4000;
      window.setTimeout(() => {
        if (!alive) return;
        setBlink(true);
        setTimeout(() => setBlink(false), 160);
        setGlance((Math.random() - 0.5) * 5);
        tick();
      }, wait);
    };
    tick();
    return () => {
      alive = false;
    };
  }, [reducedMotion]);

  const mouth = useMemo(() => {
    if (reducedMotion) return 'M 70 93 Q 90 95 110 93';
    if (emotion.mood === 'hype' || emotion.mood === 'care') return 'M 70 93 Q 90 108 110 93';
    if (emotion.mood === 'stressed') return 'M 70 98 Q 90 88 110 98';
    return 'M 70 93 Q 90 98 110 93';
  }, [emotion, reducedMotion]);

  return (
    <section className="card stage">
      <div className="aurora" style={{ opacity: 0.35 + emotion.intensity * 0.6 }} />
      <svg className={`avatar ${reducedMotion ? 'reduced' : ''} mood-${emotion.mood}`} viewBox="0 0 180 180" role="img" aria-label="Etherea avatar">
        <ellipse cx="90" cy="90" rx="52" ry="60" fill="#f5d4bc" />
        <ellipse cx="90" cy="155" rx="38" ry="20" fill="var(--accent)" opacity="0.8" />
        <ellipse cx="70" cy="80" rx="13" ry={blink ? 2 : 8} fill="#fff" />
        <ellipse cx="110" cy="80" rx="13" ry={blink ? 2 : 8} fill="#fff" />
        <circle cx={70 + glance} cy="80" r="4" fill="#111827" />
        <circle cx={110 + glance} cy="80" r="4" fill="#111827" />
        <path d={mouth} stroke="#7f1d1d" strokeWidth="4" fill="none" strokeLinecap="round" />
      </svg>
      <div className="emotion-tag">{emotion.mood}</div>
    </section>
  );
}
