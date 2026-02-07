import { computeStressFocus, runAgentAction } from "../packages/core/dist/index.js";

const checks = [];
const score = computeStressFocus({ typingPerMinute: 120, mouseMovesPerMinute: 120 });
checks.push(score.stress >= 0 && score.stress <= 100 && score.focus >= 0 && score.focus <= 100);
checks.push(Boolean(runAgentAction("create_ppt", "Demo").output));

if (checks.every(Boolean)) {
  console.log("PASS selfcheck: heuristics + agent registry");
  process.exit(0);
}
console.error("FAIL selfcheck");
process.exit(1);
