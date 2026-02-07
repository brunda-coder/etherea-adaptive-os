import { runAgentAction, stressFocus } from '../packages/core/dist/index.js';

const checks = [
  ['agent:create_ppt', !!runAgentAction('create_ppt').output],
  ['stress bounded', (() => { const r = stressFocus({ typingRate: 10, mouseVelocity: 10 }); return r.stress >= 0 && r.stress <= 100; })()]
];

let pass = true;
for (const [name, ok] of checks) {
  console.log(`${ok ? 'PASS' : 'FAIL'} ${name}`);
  if (!ok) pass = false;
}
process.exit(pass ? 0 : 1);
