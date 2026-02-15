import offlineBank from '../brain.json';
import type { BrainCommand } from './commands';

type Emotion = { mood: 'calm' | 'focused' | 'curious' | 'hype' | 'care' | 'stressed'; intensity: number };

type Intent = { patterns: string[]; responses: string[]; emotion: Emotion };
type IntentBank = { intents: Record<string, Intent>; microLines: Partial<Record<Emotion['mood'], string[]>> };

export type BrainResult = {
  response: string;
  command: BrainCommand | null;
  save_memory: Record<string, string | number | boolean> | null;
  emotion_update: Emotion;
};

const banned = [/as an ai/gi, /language model/gi, /i can.?t because i.?m ai/gi, /i am an ai/gi, /i'm an ai/gi];

const fallbackBank: IntentBank = {
  intents: {
    greeting: {
      patterns: ['^hi$', '^hello$', '^hey$'],
      responses: ['Hey. Want a quick EI demo?', 'Hi. I can run files, settings, or a mini lesson.'],
      emotion: { mood: 'care', intensity: 0.55 },
    },
    default: {
      patterns: ['.*'],
      responses: ['Tell me your target. I will route the next action.'],
      emotion: { mood: 'curious', intensity: 0.5 },
    },
  },
  microLines: {
    calm: ['Breathing steady.'],
    focused: ['Locked in.'],
    curious: ['This is interesting.'],
    hype: ['Let’s go.'],
    care: ['I am with you.'],
    stressed: ['We can keep it simple.'],
  },
};

let bankPromise: Promise<IntentBank> | null = null;

function hash(text: string) {
  return text.split('').reduce((acc, char) => (acc * 33 + char.charCodeAt(0)) >>> 0, 17);
}

function pick(seed: string, options: string[]) {
  return options[hash(seed) % options.length] ?? options[0] ?? '...';
}

async function loadBank() {
  if (!bankPromise) {
    bankPromise = fetch('/brain.json')
      .then((r) => (r.ok ? (r.json() as Promise<IntentBank>) : fallbackBank))
      .catch(() => offlineBank as IntentBank);
  }
  return bankPromise;
}

function sanitize(text: string) {
  return banned.reduce((acc, rx) => acc.replace(rx, 'Etherea'), text);
}

function clampIntensity(value: number) {
  return Math.max(0, Math.min(1, Number.isFinite(value) ? value : 0.5));
}

function teach(topic: string): string {
  return [
    `Definition: ${topic} estimates how one variable changes with another so we can predict outcomes.`,
    'Example: If study hours increase, test scores often rise. Regression helps estimate the slope of that relationship.',
    'Steps: (1) define target + features, (2) inspect data quality and outliers, (3) split train/test, (4) fit baseline model, (5) evaluate and iterate.',
    'Check questions: What does the coefficient sign tell you? How do you know if overfitting happened?',
    'Exercise: Build a tiny dataset with 8 rows, run linear regression, and explain one prediction in plain language.',
  ].join(' ');
}

function parseSettingCommand(text: string): BrainCommand | null {
  if (/toggle reduced motion/i.test(text)) return { name: 'set_theme', args: { reducedMotion: true } };
  if (/disable reduced motion/i.test(text)) return { name: 'set_theme', args: { reducedMotion: false } };
  const preset = text.match(/set theme preset\s+([\w-]+)/i);
  if (preset) return { name: 'set_theme', args: { preset: preset[1] } };
  const accent = text.match(/set accent\s+(#[0-9a-f]{6})/i);
  if (accent) return { name: 'set_theme', args: { accent: accent[1] } };
  if (/voice output on/i.test(text)) return { name: 'set_voice_output', args: { enabled: true } };
  if (/voice output off/i.test(text)) return { name: 'set_voice_output', args: { enabled: false } };
  if (/mic opt-in on|enable mic/i.test(text)) return { name: 'set_mic_opt_in', args: { enabled: true } };
  if (/mic opt-in off|disable mic/i.test(text)) return { name: 'set_mic_opt_in', args: { enabled: false } };
  return null;
}

function parseWorkspaceCommand(text: string): BrainCommand | null {
  const create = text.match(/create file\s+([^\s]+)(?:\s+with\s+([\s\S]+))?/i);
  if (create) return { name: 'create_file', args: { path: create[1], content: create[2] ?? '' } };
  const edit = text.match(/edit file\s+([^\s]+)\s+with\s+([\s\S]+)/i);
  if (edit) return { name: 'edit_file', args: { path: edit[1], content: edit[2] } };
  const summarize = text.match(/summarize file\s+([^\s]+)/i);
  if (summarize) return { name: 'summarize_file', args: { path: summarize[1] } };
  if (/^list files/i.test(text)) return { name: 'list_files', args: { depth: 4 } };
  if (/allow workspace root/i.test(text)) return { name: 'allow_workspace_root', args: {} };
  return null;
}

function parseSlash(text: string): BrainCommand | null {
  const [head, ...rest] = text.trim().slice(1).split(' ');
  const arg = rest.join(' ').trim();
  if (head === 'create') return { name: 'create_file', args: { path: arg, content: '' } };
  if (head === 'edit') return { name: 'edit_file', args: { path: arg, content: '' } };
  if (head === 'summarize') return { name: 'summarize_file', args: { path: arg } };
  if (head === 'list') return { name: 'list_files', args: { depth: 4 } };
  if (head === 'help') return { name: 'help', args: {} };
  return null;
}

export async function speak(input: string): Promise<BrainResult> {
  const text = input.trim();
  const bank = await loadBank();

  const command = text.startsWith('/') ? parseSlash(text) : parseWorkspaceCommand(text) ?? parseSettingCommand(text);

  if (/teach\s+regression/i.test(text)) {
    return {
      response: sanitize(teach('Regression')),
      command,
      save_memory: { topic: 'regression', used: true },
      emotion_update: { mood: 'focused', intensity: 0.72 },
    };
  }

  if (/what is emotional intelligence|ei intro|explain ei/i.test(text)) {
    return {
      response: sanitize(
        'Emotional intelligence means noticing state, naming it, then choosing a useful action. Etherea maps your cues to mood, adapts UI motion, and keeps the full loop local by default.',
      ),
      command,
      save_memory: { topic: 'ei_intro', used: true },
      emotion_update: { mood: 'care', intensity: 0.62 },
    };
  }

  const selected =
    Object.values(bank.intents).find((intent) => intent.patterns.some((pattern) => new RegExp(pattern, 'i').test(text))) ?? bank.intents.default;
  const line = bank.microLines?.[selected.emotion.mood]?.[hash(text) % (bank.microLines[selected.emotion.mood]?.length ?? 1)] ?? '';

  return {
    response: sanitize(`${pick(text, selected.responses)} ${line}`.trim()),
    command,
    save_memory: { last_intent_mood: selected.emotion.mood, ts: Date.now() },
    emotion_update: { mood: selected.emotion.mood, intensity: clampIntensity(selected.emotion.intensity) },
  };
}
