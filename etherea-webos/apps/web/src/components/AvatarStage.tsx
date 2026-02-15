import { useEffect, useMemo, useState } from 'react';

export type Emotion = { mood: 'calm' | 'focused' | 'curious' | 'hype' | 'care' | 'stressed'; intensity: number };

type Palette = { skin: string; outfitA: string; outfitB: string; aura: string; hair: string };

const PALETTES: Palette[] = [
  { skin: '#f6d7c6', outfitA: '#7c3aed', outfitB: '#312e81', aura: '#8b5cf6', hair: '#1f2937' },
  { skin: '#efc9b5', outfitA: '#f97316', outfitB: '#7c2d12', aura: '#fb923c', hair: '#292524' },
  { skin: '#e6b89f', outfitA: '#06b6d4', outfitB: '#0e7490', aura: '#22d3ee', hair: '#111827' },
  { skin: '#dba585', outfitA: '#22c55e', outfitB: '#166534', aura: '#4ade80', hair: '#172554' },
];

export function AvatarStage({ emotion, reducedMotion }: { emotion: Emotion; reducedMotion: boolean }) {
  const [blink, setBlink] = useState(false);
  const [glance, setGlance] = useState({ x: 0, y: 0 });
  const [paletteIndex, setPaletteIndex] = useState(0);
  const [twirl, setTwirl] = useState(false);

  useEffect(() => {
    if (reducedMotion) return;
    let canceled = false;
    const scheduleBlink = () => {
      const delay = 3000 + Math.random() * 4000;
      const id = window.setTimeout(() => {
        if (canceled) return;
        setBlink(true);
        setTimeout(() => setBlink(false), 140);
        setGlance({ x: (Math.random() - 0.5) * 6, y: (Math.random() - 0.5) * 3 });
        scheduleBlink();
      }, delay);
      return id;
    };

    const timer = scheduleBlink();
    return () => {
      canceled = true;
      clearTimeout(timer);
    };
  }, [reducedMotion]);

  const expression = useMemo(() => {
    if (emotion.mood === 'hype') return { brow: -4, mouth: 'M 82 156 Q 110 182 138 156' };
    if (emotion.mood === 'focused') return { brow: 3, mouth: 'M 84 156 Q 110 160 136 156' };
    if (emotion.mood === 'care') return { brow: -1, mouth: 'M 84 156 Q 110 170 136 156' };
    if (emotion.mood === 'stressed') return { brow: 5, mouth: 'M 84 164 Q 110 148 136 164' };
    if (emotion.mood === 'curious') return { brow: -2, mouth: 'M 84 156 Q 110 166 136 156' };
    return { brow: 0, mouth: 'M 84 156 Q 110 162 136 156' };
  }, [emotion.mood]);

  const palette = PALETTES[paletteIndex % PALETTES.length];

  return (
    <section className="stage">
      <div className="aura-ring" style={{ opacity: 0.35 + emotion.intensity * 0.6, animationDuration: `${3.6 - emotion.intensity * 1.7}s`, background: `radial-gradient(circle, ${palette.aura}, transparent 68%)` }} />
      <svg className={`avatar ${twirl ? 'twirl' : ''}`} viewBox="0 0 240 300" role="img" aria-label="Etherea avatar">
        <defs>
          <radialGradient id="faceGrad" cx="50%" cy="34%" r="68%">
            <stop offset="0%" stopColor="#fff" stopOpacity="0.3" />
            <stop offset="100%" stopColor={palette.skin} />
          </radialGradient>
          <linearGradient id="hoodGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={palette.outfitA} />
            <stop offset="100%" stopColor={palette.outfitB} />
          </linearGradient>
        </defs>
        <ellipse className="stage-shadow" cx="120" cy="280" rx="62" ry="16" />
        <g className="avatar-float">
          <g className="avatar-breathe">
            <path d="M64 274 Q120 208 176 274 L176 292 L64 292 Z" fill="url(#hoodGrad)" />
            <ellipse cx="120" cy="138" rx="58" ry="72" fill="url(#faceGrad)" />
            <path d="M60 128 Q80 46 120 52 Q160 46 180 128 Q158 96 120 98 Q82 96 60 128 Z" fill={palette.hair} />
            <path d={`M84 112 Q98 ${102 + expression.brow} 110 110`} stroke="#111827" strokeWidth="4" fill="none" strokeLinecap="round" />
            <path d={`M130 110 Q142 ${102 + expression.brow} 156 112`} stroke="#111827" strokeWidth="4" fill="none" strokeLinecap="round" />
            <ellipse cx="95" cy="136" rx="14" ry={blink ? 2 : 10} fill="#fff" />
            <ellipse cx="145" cy="136" rx="14" ry={blink ? 2 : 10} fill="#fff" />
            <circle cx={95 + glance.x} cy={136 + glance.y} r="4.5" fill="#111827" />
            <circle cx={145 + glance.x} cy={136 + glance.y} r="4.5" fill="#111827" />
            <path d={expression.mouth} stroke="#7f1d1d" strokeWidth="4" fill="none" strokeLinecap="round" />
          </g>
        </g>
      </svg>
      <button
        className="twirl-btn"
        onClick={() => {
          if (reducedMotion) {
            setPaletteIndex((index) => (index + 1) % PALETTES.length);
            return;
          }
          setTwirl(true);
          window.setTimeout(() => {
            setPaletteIndex((index) => (index + 1) % PALETTES.length);
            setTwirl(false);
          }, 650);
        }}
      >
        Twirl style
      </button>
    </section>
  );
}
