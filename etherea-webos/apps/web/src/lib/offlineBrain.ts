import brainData from '../brain.json';
import type { EthereaEmotion } from '../components/AvatarStage';

export type BrainOutput = {
  response: string;
  command: string;
  save_memory: boolean;
  emotion_update: EthereaEmotion;
};

type BrainKnowledge = {
  variants: Record<string, string[]>;
  teach_regression: {
    lesson: string[];
    example: string;
    quick_questions: string[];
    exercise: string;
  };
  ei_intro: string;
  low_internet_style: string;
  banned_phrases: string[];
  fallback: BrainOutput;
};

const knowledge = brainData as BrainKnowledge;
const emotionCycle: EthereaEmotion[] = ['calm', 'curious', 'hype', 'care', 'focused', 'stressed'];

function seedFromInput(input: string): number {
  let hash = 0;
  for (const char of input.toLowerCase()) hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  return hash;
}

function chooseVariant(input: string, key: keyof BrainKnowledge['variants']): string {
  const pool = knowledge.variants[key] ?? knowledge.variants.default;
  const seed = seedFromInput(`${key}:${input}`);
  return pool[seed % pool.length];
}

function cleanCharacterVoice(text: string): string {
  let clean = text;
  for (const phrase of knowledge.banned_phrases) {
    const pattern = new RegExp(phrase, 'ig');
    clean = clean.replace(pattern, '');
  }
  return clean.replace(/\s{2,}/g, ' ').trim();
}

function nextEmotion(input: string): EthereaEmotion {
  const seed = seedFromInput(input);
  return emotionCycle[seed % emotionCycle.length];
}

function teachRegressionResponse(): string {
  const lines = knowledge.teach_regression.lesson.map((line, index) => `${index + 1}. ${line}`);
  return [
    'Regression quick lesson:',
    ...lines,
    `Example: ${knowledge.teach_regression.example}`,
    'Quick questions:',
    `- ${knowledge.teach_regression.quick_questions[0]}`,
    `- ${knowledge.teach_regression.quick_questions[1]}`,
    `Exercise: ${knowledge.teach_regression.exercise}`,
  ].join('\n');
}

export function runOfflineBrain(input: string): BrainOutput {
  const text = input.trim();
  if (!text) return knowledge.fallback;

  const normalized = text.toLowerCase();
  let response = '';
  let command = 'reply';
  let emotion: EthereaEmotion = nextEmotion(normalized);

  if (normalized.includes('teach regression')) {
    response = teachRegressionResponse();
    command = 'teach_regression';
    emotion = 'focused';
  } else if (normalized.includes('emotional intelligence') || normalized === 'ei' || normalized.includes('ei intro')) {
    response = `${knowledge.ei_intro}\n${knowledge.low_internet_style}`;
    command = 'ei_intro';
    emotion = 'care';
  } else if (normalized.includes('speak demo')) {
    response = chooseVariant(normalized, 'speak_demo');
    command = 'speak_demo';
    emotion = 'curious';
  } else {
    response = `${chooseVariant(normalized, 'default')} ${knowledge.low_internet_style}`;
  }

  return {
    response: cleanCharacterVoice(response),
    command,
    save_memory: true,
    emotion_update: emotion,
  };
}
