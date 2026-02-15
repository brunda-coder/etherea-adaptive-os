import type { BrainCommand } from './commands';

type Emotion = { mood: 'calm' | 'focused' | 'curious' | 'hype' | 'care' | 'stressed'; intensity: number };

type IntentBank = {
  intents: Record<string, { patterns: string[]; responses: string[]; emotion: Emotion }>;
};

export type BrainResult = {
  response: string;
  command: BrainCommand | null;
  save_memory: boolean;
  emotion_update: Emotion;
};

const banned = [/as an ai/gi, /language model/gi];

let bankPromise: Promise<IntentBank> | null = null;

function hash(text: string) {
  return text.split('').reduce((acc, char) => (acc * 31 + char.charCodeAt(0)) >>> 0, 7);
}

function pick(text: string, options: string[]) {
  return options[hash(text) % options.length] ?? options[0] ?? '...';
}

async function loadBank() {
  if (!bankPromise) {
    bankPromise = fetch('/brain.json').then((r) => r.json() as Promise<IntentBank>);
  }
  return bankPromise;
}

function sanitize(text: string) {
  return banned.reduce((acc, rx) => acc.replace(rx, 'Etherea'), text);
}

function slashToCommand(input: string): BrainCommand | null {
  const [head, ...rest] = input.trim().slice(1).split(' ');
  const argText = rest.join(' ').trim();
  if (head === 'create') return { name: 'create_file', args: { path: argText, content: '' } };
  if (head === 'edit') return { name: 'edit_file', args: { path: argText, content: '' } };
  if (head === 'summarize') return { name: 'summarize_file', args: { path: argText } };
  if (head === 'list') return { name: 'list_files', args: { depth: 5 } };
  if (head === 'theme') return { name: 'set_theme', args: { preset: argText } };
  if (head === 'motion') return { name: 'set_theme', args: { reducedMotion: argText.includes('on') } };
  return null;
}

function parseNatural(text: string): BrainCommand | null {
  const create = text.match(/create file\s+([^\s]+)\s+with\s+([\s\S]+)/i);
  if (create) return { name: 'create_file', args: { path: create[1], content: create[2] } };
  const edit = text.match(/edit file\s+([^\s]+)\s+with\s+([\s\S]+)/i);
  if (edit) return { name: 'edit_file', args: { path: edit[1], content: edit[2] } };
  const summarize = text.match(/summarize file\s+([^\s]+)/i);
  if (summarize) return { name: 'summarize_file', args: { path: summarize[1] } };
  if (/^list files/i.test(text)) return { name: 'list_files', args: { depth: 5 } };
  const theme = text.match(/switch theme\s+([\w-]+)/i);
  if (theme) return { name: 'set_theme', args: { preset: theme[1] } };
  if (/^help$/i.test(text)) return { name: 'help', args: {} };
  return null;
}

function teach(topic: string): string {
  return `Definition: ${topic} predicts how changes in one variable relate to another.\nIntuition: think of drawing the best-fit line through noisy points.\nExample: if hours studied rises by 1 and score rises by 5, slope is +5.\nQuestions: 1) What does slope mean? 2) What does intercept mean?\nExercise: Build a tiny dataset for ${topic} and estimate a trend line.`;
}

export async function speak(input: string): Promise<BrainResult> {
  const text = input.trim();
  const bank = await loadBank();
  const slash = text.startsWith('/') ? slashToCommand(text) : null;
  const natural = slash ? null : parseNatural(text);
  const command = slash ?? natural;

  if (/teach\s+regression/i.test(text)) {
    return {
      response: teach('regression'),
      command,
      save_memory: true,
      emotion_update: { mood: 'focused', intensity: 0.62 },
    };
  }
  const teachAny = text.match(/^teach\s+(.+)/i);
  if (teachAny) {
    return {
      response: teach(teachAny[1]),
      command,
      save_memory: true,
      emotion_update: { mood: 'curious', intensity: 0.64 },
    };
  }

  const intent = Object.values(bank.intents).find((i) => i.patterns.some((p) => new RegExp(p, 'i').test(text))) ?? bank.intents.default;
  return {
    response: sanitize(pick(text, intent.responses)),
    command,
    save_memory: true,
    emotion_update: intent.emotion,
  };
}
