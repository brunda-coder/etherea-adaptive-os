export type ThemePreset = 'nebula' | 'cotton-candy' | 'forest' | 'sunset' | 'midnight';

export type ThemeSettings = {
  preset: ThemePreset;
  accent: string;
  glow: number;
  rounded: number;
  reducedMotion: boolean;
  sensorsKillSwitch: boolean;
  mode: 'professional' | 'balanced' | 'playful';
};

const STORAGE_KEY = 'etherea.theme.v1';

export const PRESET_ACCENTS: Record<ThemePreset, string> = {
  nebula: '#7c3aed',
  'cotton-candy': '#ec4899',
  forest: '#22c55e',
  sunset: '#f97316',
  midnight: '#38bdf8',
};

export const defaultTheme: ThemeSettings = {
  preset: 'nebula',
  accent: PRESET_ACCENTS.nebula,
  glow: 0.55,
  rounded: 14,
  reducedMotion: false,
  sensorsKillSwitch: false,
  mode: 'professional',
};

export function loadTheme(): ThemeSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultTheme;
    const parsed = JSON.parse(raw) as Partial<ThemeSettings>;
    return {
      ...defaultTheme,
      ...parsed,
      accent: parsed.accent ?? PRESET_ACCENTS[(parsed.preset as ThemePreset) ?? defaultTheme.preset],
    };
  } catch {
    return defaultTheme;
  }
}

export function saveTheme(next: ThemeSettings) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
}

export function applyTheme(theme: ThemeSettings) {
  const root = document.documentElement;
  root.style.setProperty('--accent', theme.accent);
  root.style.setProperty('--glow', String(theme.glow));
  root.style.setProperty('--rounded', `${theme.rounded}px`);
  document.body.dataset.reduceMotion = theme.reducedMotion ? 'on' : 'off';
}
