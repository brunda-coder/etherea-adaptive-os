import test from 'node:test';
import assert from 'node:assert/strict';
import { stressFocus } from '../heuristics.js';

test('stress/focus bounds stay in range', () => {
  const { stress, focus } = stressFocus({ typingRate: 1000, mouseVelocity: 1000 });
  assert.ok(stress >= 0 && stress <= 100);
  assert.ok(focus >= 0 && focus <= 100);
});
