import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, '..');

const distIndex = path.join(repoRoot, 'apps/web/dist/index.html');
const viteConfig = path.join(repoRoot, 'apps/web/vite.config.ts');

function fail(message) {
  console.error(`SELF-CHECK FAIL: ${message}`);
  process.exit(1);
}

if (!fs.existsSync(distIndex)) {
  fail('missing apps/web/dist/index.html (build likely did not run or failed)');
}

const viteText = fs.readFileSync(viteConfig, 'utf8');
const requiredSnippets = [
  'maximumFileSizeToCacheInBytes',
  '8 * 1024 * 1024',
  'manualChunks',
  'globIgnores',
];

for (const snippet of requiredSnippets) {
  if (!viteText.includes(snippet)) {
    fail(`vite config is missing required precache safety snippet: ${snippet}`);
  }
}

console.log('SELF-CHECK PASS: web dist output + workbox/rollup precache safety checks');
