import fs from 'node:fs';
import path from 'node:path';

const appPath = path.resolve('apps/web/src/App.tsx');
const heurPath = path.resolve('packages/core/src/heuristics.ts');
const regPath = path.resolve('packages/core/src/registry.ts');
const appText = fs.readFileSync(appPath, 'utf8');
const heurText = fs.readFileSync(heurPath, 'utf8');
const regText = fs.readFileSync(regPath, 'utf8');

const checks = [
  ['indexeddb save/load pathway exists', appText.includes('indexedDB.open') && appText.includes('idbSet') && appText.includes('idbGet')],
  ['agent:create_ppt structured', regText.includes('create_ppt') && regText.includes('outline')],
  ['agent:summarize_pdf structured', regText.includes('summarize_pdf') && regText.includes('summary')],
  ['agent:generate_notes structured', regText.includes('generate_notes') && regText.includes('notes')],
  ['stress/focus heuristic exists', heurText.includes('stressFocus') && heurText.includes('typingRate')],
  ['mic permission pathway exists', appText.includes('getUserMedia')],
  ['3d avatar loaded indicator exists', appText.includes('avatar loaded') && appText.includes('THREE.')],
];

let pass = true;
for (const [name, ok] of checks) {
  console.log(`${ok ? 'PASS' : 'FAIL'} ${name}`);
  if (!ok) pass = false;
}
process.exit(pass ? 0 : 1);
