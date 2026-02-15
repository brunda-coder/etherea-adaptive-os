import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, '..');

const appPath = path.join(repoRoot, 'apps/web/src/App.tsx');
const avatarPath = path.join(repoRoot, 'apps/web/src/components/AvatarStage.tsx');
const brainEnginePath = path.join(repoRoot, 'apps/web/src/lib/offlineBrain.ts');
const heurPath = path.join(repoRoot, 'packages/core/src/heuristics.ts');
const regPath = path.join(repoRoot, 'packages/core/src/registry.ts');
const appText = fs.readFileSync(appPath, 'utf8');
const avatarText = fs.readFileSync(avatarPath, 'utf8');
const engineText = fs.readFileSync(brainEnginePath, 'utf8');
const heurText = fs.readFileSync(heurPath, 'utf8');
const regText = fs.readFileSync(regPath, 'utf8');

const checks = [
  ['indexeddb save/load pathway exists', appText.includes('indexedDB.open') && appText.includes('idbSet') && appText.includes('idbGet')],
  ['agent:create_ppt structured', regText.includes('create_ppt') && regText.includes('outline')],
  ['agent:summarize_pdf structured', regText.includes('summarize_pdf') && regText.includes('summary')],
  ['agent:generate_notes structured', regText.includes('generate_notes') && regText.includes('notes')],
  ['stress/focus heuristic exists', heurText.includes('stressFocus') && heurText.includes('typingRate')],
  ['mic permission pathway exists', appText.includes('getUserMedia') && appText.includes("'requesting'") && appText.includes("'blocked'")],
  ['procedural avatar stage exists', avatarText.includes('AvatarStage') && avatarText.includes('costume-spin')],
  ['offline brain engine exists', engineText.includes('teachRegressionResponse') && engineText.includes('runOfflineBrain')],
];

let pass = true;
for (const [name, ok] of checks) {
  console.log(`${ok ? 'PASS' : 'FAIL'} ${name}`);
  if (!ok) pass = false;
}
process.exit(pass ? 0 : 1);
