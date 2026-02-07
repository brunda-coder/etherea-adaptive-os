export interface StressInput {
  typingRate: number;
  mouseVelocity: number;
}

export function stressFocus({ typingRate, mouseVelocity }: StressInput): { stress: number; focus: number } {
  const stress = Math.max(0, Math.min(100, Math.round(typingRate * 0.6 + mouseVelocity * 0.4)));
  const focus = Math.max(0, Math.min(100, 100 - Math.round(Math.abs(typingRate - 35) * 1.1 + mouseVelocity * 0.2)));
  return { stress, focus };
}
