import React from 'react';
import './candy.css';

export const CandyButton = ({ children, onClick, id }) => (
  <button id={id} className="candy-button" onClick={onClick}>
    {children}
  </button>
);

export const CandyCard = ({ children, id }) => (
  <div id={id} className="candy-card">
    {children}
  </div>
);

export const CandyChip = ({ children }) => (
  <div className="candy-chip">{children}</div>
);

export const CandyTooltipBubble = ({ text, style }) => (
  <div className="candy-tooltip-bubble" style={style}>
    {text}
  </div>
);

export const CandySpotlightOverlay = ({ action, onEnd }) => {
  const [rect, setRect] = React.useState(null);

  React.useEffect(() => {
    const target = document.getElementById(action.targetId);
    if (target) {
      setRect(target.getBoundingClientRect());
    } else {
      // If target is not found, show a toast.
      // In a real app, you'd use a proper toast library.
      alert(`Toast: Can't find element "${action.targetId}"`);
      onEnd(); // End the action so the app can proceed
    }
  }, [action.targetId, onEnd]);

  if (!rect) return null;

  const spotlightStyle = {
    top: rect.top - 12,
    left: rect.left - 12,
    width: rect.width + 24,
    height: rect.height + 24,
    borderRadius: '1.5rem'
  };

  const tooltipStyle = {
    top: rect.top,
    left: rect.left + rect.width / 2,
  };

  return (
    <div className="spotlight-overlay">
      <div className={`spotlight-target ${action.style || 'candyGlow'}`} style={spotlightStyle}></div>
      {action.text && <CandyTooltipBubble text={action.text} style={tooltipStyle} />}
    </div>
  );
};


export const AuroraRing = ({ isSpeaking, expression }) => {
    const moodClass = `mood-${expression?.mood || 'calm'}`;
    return <div className={`aurora-ring ${isSpeaking ? 'pulsing' : ''} ${moodClass}`}></div>;
};
