import { useEffect, useMemo, useState } from 'react';

export type Emotion = { mood: 'calm' | 'focused' | 'curious' | 'hype' | 'care' | 'stressed'; intensity: number };

const SKINS = ['#f8d7c3', '#e8b99a', '#c98f73', '#a56b52', '#7d4f3b'];
const HAIR = ['#25161b', '#3c2a20', '#1f2937'];
const OUTFITS = ['#7c3aed', '#ec4899', '#22c55e', '#f97316', '#38bdf8'];

export function AvatarStage({ emotion, reducedMotion }: { emotion: Emotion; reducedMotion: boolean }) {
  const [blink, setBlink] = useState(false);
  const [glance, setGlance] = useState(0);
  const [lookUp, setLookUp] = useState(0);
  const [styleIndex, setStyleIndex] = useState(0);
  const [twirl, setTwirl] = useState(false);

  useEffect(() => {
    if (reducedMotion) return;
    let alive = true;
    const timer = () => {
      const delay = 3000 + Math.random() * 4000;
      window.setTimeout(() => {
        if (!alive) return;
        setBlink(true);
        setTimeout(() => setBlink(false), 160);
        setGlance((Math.random() - 0.5) * 6);
        setLookUp((Math.random() - 0.5) * 3);
        timer();
      }, delay);
    };
    timer();
    return () => {
      alive = false;
    };
  }, [reducedMotion]);

  useEffect(() => {
    if (reducedMotion || emotion.mood !== 'hype') return;
    setTwirl(true);
    const id = setTimeout(() => {
      setStyleIndex((i) => (i + 1) % OUTFITS.length);
      setTwirl(false);
    }, 620);
    return () => clearTimeout(id);
  }, [emotion.mood, reducedMotion]);

  const expression = useMemo(() => {
    if (emotion.mood === 'care') return { brow: -2, mouth: 'M 70 112 Q 90 124 110 112' };
    if (emotion.mood === 'hype') return { brow: -4, mouth: 'M 68 110 Q 90 132 112 110' };
    if (emotion.mood === 'stressed') return { brow: 5, mouth: 'M 72 118 Q 90 103 108 118' };
    if (emotion.mood === 'focused') return { brow: 2, mouth: 'M 72 114 Q 90 116 108 114' };
    if (emotion.mood === 'curious') return { brow: -1, mouth: 'M 72 113 Q 90 121 108 113' };
    return { brow: 0, mouth: 'M 72 114 Q 90 119 108 114' };
  }, [emotion.mood]);

  return (
    <section className="card stage">
      <div className="aura-ring" style={{ opacity: 0.3 + emotion.intensity * 0.7, animationDuration: `${3.4 - emotion.intensity * 1.5}s` }} />
      <svg className={`avatar ${reducedMotion ? 'reduced' : ''} ${twirl ? 'twirl' : ''}`} viewBox="0 0 220 260" role="img" aria-label="Etherea avatar">
        <defs>
          <radialGradient id="skin-grad" cx="50%" cy="35%" r="60%">
            <stop offset="0%" stopColor="#fff" stopOpacity="0.28" />
            <stop offset="100%" stopColor={SKINS[styleIndex % SKINS.length]} />
          </radialGradient>
          <linearGradient id="hoodie-grad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={OUTFITS[styleIndex % OUTFITS.length]} />
            <stop offset="100%" stopColor="#111827" />
          </linearGradient>
        </defs>
        <ellipse cx="110" cy="236" rx="62" ry="14" fill="#020617" opacity="0.55" />
        <g className="avatar-breathe">
          <path d="M60 226 Q110 184 160 226 L160 252 L60 252 Z" fill="url(#hoodie-grad)" />
          <ellipse cx="110" cy="120" rx="54" ry="60" fill="url(#skin-grad)" />
          <path d="M62 115 Q82 48 110 52 Q138 48 158 115 Q132 90 110 92 Q88 90 62 115 Z" fill={HAIR[styleIndex % HAIR.length]} />
          <path d={`M76 92 Q90 ${84 + expression.brow} 102 90`} stroke="#1f2937" strokeWidth="4" fill="none" strokeLinecap="round" />
          <path d={`M118 90 Q130 ${84 + expression.brow} 144 92`} stroke="#1f2937" strokeWidth="4" fill="none" strokeLinecap="round" />
          <ellipse cx="88" cy="112" rx="14" ry={blink ? 2 : 9} fill="#fff" />
          <ellipse cx="132" cy="112" rx="14" ry={blink ? 2 : 9} fill="#fff" />
          <circle cx={88 + glance} cy={112 + lookUp} r="4" fill="#111827" />
          <circle cx={132 + glance} cy={112 + lookUp} r="4" fill="#111827" />
          <path d={expression.mouth} stroke="#7f1d1d" strokeWidth="4" fill="none" strokeLinecap="round" />
          <path d="M84 136 Q110 152 136 136" stroke="#d97706" strokeOpacity="0.4" strokeWidth="2" fill="none" />
        </g>
      </svg>
      <div className="emotion-tag">{emotion.mood}</div>
    </section>
  );
}
