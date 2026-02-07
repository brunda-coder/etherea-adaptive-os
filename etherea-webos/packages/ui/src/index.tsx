import React from 'react';

export function AuroraRing({ stress }: { stress: number }) {
  const color = stress > 70 ? '#ef4444' : '#6ee7ff';
  return <div style={{ width: 180, height: 180, borderRadius: '50%', border: `8px solid ${color}`, boxShadow: `0 0 40px ${color}` }} />;
}

export function AvatarFace({ mouthOpen, expression }: { mouthOpen: number; expression: string }) {
  return (
    <svg width="140" height="140" viewBox="0 0 140 140" role="img" aria-label="Etherea avatar">
      <circle cx="70" cy="70" r="58" fill="#1a213c" stroke="#84ccff" strokeWidth="4" />
      <circle cx="50" cy="58" r="7" fill="#fff" />
      <circle cx="90" cy="58" r="7" fill="#fff" />
      <ellipse cx="70" cy="92" rx="16" ry={Math.max(2, mouthOpen)} fill="#fca5a5" />
      <text x="70" y="132" fontSize="10" fill="#dbeafe" textAnchor="middle">{expression}</text>
    </svg>
  );
}
