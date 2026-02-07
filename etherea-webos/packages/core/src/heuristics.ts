export interface InputSignals {
  typingPerMinute: number;
  mouseMovesPerMinute: number;
}

export interface StressFocusScore {
  stress: number;
  focus: number;
}

const clamp = (value: number) => Math.max(0, Math.min(100, value));

export function computeStressFocus({ typingPerMinute, mouseMovesPerMinute }: InputSignals): StressFocusScore {
  const stress = clamp(typingPerMinute * 0.7 + mouseMovesPerMinute * 0.25 - 20);
  const focus = clamp(100 - Math.abs(typingPerMinute - 180) * 0.2 - mouseMovesPerMinute * 0.08);
  return { stress, focus };
}
