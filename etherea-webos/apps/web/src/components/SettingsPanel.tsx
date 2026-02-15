import { PRESET_ACCENTS, type ThemeSettings } from '../lib/theme';

export function SettingsPanel({ theme, onTheme }: { theme: ThemeSettings; onTheme: (theme: ThemeSettings) => void }) {
  return (
    <section className="card settings">
      <h3>Settings</h3>
      <label>
        Preset
        <select
          value={theme.preset}
          onChange={(e) => onTheme({ ...theme, preset: e.target.value as ThemeSettings['preset'], accent: PRESET_ACCENTS[e.target.value as ThemeSettings['preset']] })}
        >
          {Object.keys(PRESET_ACCENTS).map((preset) => (
            <option key={preset}>{preset}</option>
          ))}
        </select>
      </label>
      <label>
        Accent
        <input value={theme.accent} onChange={(e) => onTheme({ ...theme, accent: e.target.value })} placeholder="#7c3aed" />
      </label>
      <label>
        Glow {theme.glow.toFixed(2)}
        <input type="range" min="0" max="1" step="0.05" value={theme.glow} onChange={(e) => onTheme({ ...theme, glow: Number(e.target.value) })} />
      </label>
      <label>
        Rounded {theme.rounded}px
        <input type="range" min="4" max="28" step="1" value={theme.rounded} onChange={(e) => onTheme({ ...theme, rounded: Number(e.target.value) })} />
      </label>
      <label>
        Reduced motion
        <input type="checkbox" checked={theme.reducedMotion} onChange={(e) => onTheme({ ...theme, reducedMotion: e.target.checked })} />
      </label>
      <label>
        Voice output (TTS)
        <input type="checkbox" checked={theme.voiceOutputEnabled} onChange={(e) => onTheme({ ...theme, voiceOutputEnabled: e.target.checked })} />
      </label>
      <label>
        Mic opt-in (OFF by default)
        <input
          type="checkbox"
          checked={theme.micOptIn}
          onChange={(e) => onTheme({ ...theme, micOptIn: e.target.checked, privacyKillSwitch: e.target.checked ? false : theme.privacyKillSwitch })}
        />
      </label>
      <label>
        Privacy kill switch (forces mic OFF)
        <input type="checkbox" checked={theme.privacyKillSwitch} onChange={(e) => onTheme({ ...theme, privacyKillSwitch: e.target.checked, micOptIn: e.target.checked ? false : theme.micOptIn })} />
      </label>
      <label>
        Sensors master kill switch
        <input type="checkbox" checked={theme.sensorsKillSwitch} onChange={(e) => onTheme({ ...theme, sensorsKillSwitch: e.target.checked })} />
      </label>
      <p>Offline-first brain · mic never starts on load · explicit opt-in required.</p>
    </section>
  );
}
