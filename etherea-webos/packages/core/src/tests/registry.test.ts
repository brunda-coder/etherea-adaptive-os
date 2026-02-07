import test from 'node:test';
import assert from 'node:assert/strict';
import { runAgentAction } from '../registry.js';

test('agent actions produce structured output', () => {
  const result = runAgentAction('create_ppt');
  assert.equal(result.task, 'create_ppt');
  assert.ok(Array.isArray(result.plan));
  assert.ok('outline' in result.output);
});
