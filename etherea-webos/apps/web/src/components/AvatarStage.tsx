import { useMemo, type CSSProperties } from 'react';

export type EthereaEmotion = 'calm' | 'curious' | 'hype' | 'care' | 'focused' | 'stressed';

type AvatarStageProps = {
  emotion?: string;
  speaking?: boolean;
  reducedMotion?: boolean;
  costumeSpinKey?: number;
  glowIntensity?: number;
};

type EmotionVisual = {
  browY: number;
  mouthCurve: string;
  halo: number;
  speed: number;
  pupilX: number;
};

const EMOTION_MAP: Record<EthereaEmotion, EmotionVisual> = {
  calm: { browY: 0, mouthCurve: 'M 104 132 Q 128 146 152 132', halo: 0.25, speed: 1, pupilX: 0 },
  curious: { browY: -4, mouthCurve: 'M 104 132 Q 128 152 152 132', halo: 0.35, speed: 0.92, pupilX: 2.2 },
  hype: { browY: -6, mouthCurve: 'M 102 130 Q 128 160 154 130', halo: 0.6, speed: 1.2, pupilX: 0.6 },
  care: { browY: 1, mouthCurve: 'M 106 134 Q 128 144 150 134', halo: 0.45, speed: 0.86, pupilX: -1 },
  focused: { browY: 3, mouthCurve: 'M 108 132 Q 128 136 148 132', halo: 0.3, speed: 0.8, pupilX: 0 },
  stressed: { browY: 7, mouthCurve: 'M 106 138 Q 128 130 150 138', halo: 0.22, speed: 1.35, pupilX: -2 },
};

function normalizeEmotion(value?: string): EthereaEmotion {
  const key = (value ?? 'calm').toLowerCase() as EthereaEmotion;
  return key in EMOTION_MAP ? key : 'calm';
}

export function AvatarStage({ emotion, speaking = false, reducedMotion = false, costumeSpinKey = 0, glowIntensity = 0.5 }: AvatarStageProps) {
  const normalizedEmotion = normalizeEmotion(emotion);
  const visual = EMOTION_MAP[normalizedEmotion];

  const style = useMemo(
    () =>
      ({
        ['--avatar-halo' as string]: String(Math.min(1, visual.halo + glowIntensity * 0.2)),
        ['--avatar-speed' as string]: reducedMotion ? '0s' : `${Math.max(0.5, visual.speed)}s`,
        ['--avatar-glance-x' as string]: `${visual.pupilX}px`,
      }) as CSSProperties,
    [glowIntensity, reducedMotion, visual.halo, visual.pupilX, visual.speed],
  );

  const costumeClass = reducedMotion ? 'avatar-costume' : `avatar-costume costume-spin-${costumeSpinKey % 2}`;
  const wrapperClass = `avatar-stage ${reducedMotion ? 'motion-off' : ''} ${speaking ? 'is-speaking' : ''}`;

  return (
    <div className={wrapperClass} style={style} aria-label={`Etherea avatar ${normalizedEmotion}`}>
      <svg viewBox="0 0 256 256" role="img" aria-hidden="true">
        <defs>
          <radialGradient id="avatarHalo" cx="50%" cy="40%" r="50%">
            <stop offset="0%" stopColor="rgba(103,232,249,0.55)" />
            <stop offset="100%" stopColor="rgba(103,232,249,0)" />
          </radialGradient>
        </defs>

        <ellipse className="halo" cx="128" cy="126" rx="90" ry="92" fill="url(#avatarHalo)" />

        <g className="avatar-float avatar-breathe">
          <ellipse className="ear" cx="69" cy="108" rx="14" ry="20" />
          <ellipse className="ear" cx="187" cy="108" rx="14" ry="20" />

          <path className="hair" d="M66 106 C66 60 100 40 130 40 C163 40 193 66 190 106 C180 82 160 69 128 69 C95 69 80 84 66 106Z" />
          <circle className="head" cx="128" cy="116" r="62" />

          <g transform={`translate(0 ${visual.browY})`}>
            <path className="brow" d="M88 101 Q104 91 120 101" />
            <path className="brow" d="M136 101 Q152 91 168 101" />
          </g>

          <g className="eye blink" transform="translate(98 114)">
            <ellipse rx="12" ry="9" />
            <circle className="pupil glance" cx="0" cy="0" r="4.5" />
          </g>
          <g className="eye blink" transform="translate(158 114)">
            <ellipse rx="12" ry="9" />
            <circle className="pupil glance" cx="0" cy="0" r="4.5" />
          </g>

          <path className="mouth smile" d={visual.mouthCurve} />

          <g className={costumeClass}>
            <path className="hoodie" d="M65 172 C82 150 102 143 128 143 C154 143 174 150 191 172 L202 216 H54 Z" />
            <path className="hoodie-shade" d="M83 172 C95 160 111 153 128 153 C145 153 161 160 173 172 L176 195 H80 Z" />
            <rect className="zip" x="124" y="155" width="8" height="53" rx="4" />
          </g>
        </g>
      </svg>
    </div>
  );
}
