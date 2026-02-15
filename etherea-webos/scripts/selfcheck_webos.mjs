import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, '..');

const distIndex = path.join(repoRoot, 'apps/web/dist/index.html');
const viteConfig = path.join(repoRoot, 'apps/web/vite.config.ts');
const brainPath = path.join(repoRoot, 'apps/web/src/brain.json');

function fail(message) {
  console.error(`SELF-CHECK FAIL: ${message}`);
  process.exit(1);
}

if (!fs.existsSync(distIndex)) {
  fail('missing apps/web/dist/index.html (build likely did not run or failed)');
}

const viteText = fs.readFileSync(viteConfig, 'utf8');
const requiredSnippets = ['maximumFileSizeToCacheInBytes', '8 * 1024 * 1024', 'manualChunks', 'globIgnores'];

for (const snippet of requiredSnippets) {
  if (!viteText.includes(snippet)) {
    fail(`vite config is missing required precache safety snippet: ${snippet}`);
  }
}

if (!fs.existsSync(brainPath)) {
  fail('missing apps/web/src/brain.json offline brain contract');
}

const brain = JSON.parse(fs.readFileSync(brainPath, 'utf8'));
for (const key of ['response', 'command', 'save_memory', 'emotion_update']) {
  if (!(key in brain)) {
    fail(`brain.json missing required field: ${key}`);
  }
}

const webSrc = fs.readFileSync(path.join(repoRoot, 'apps/web/src/App.tsx'), 'utf8');
if (/gemini|googlegenerativeai/i.test(webSrc)) {
  fail('runtime Gemini reference detected in apps/web/src/App.tsx');
}

console.log('SELF-CHECK PASS: web dist output + workbox/rollup safety + offline brain contract');
