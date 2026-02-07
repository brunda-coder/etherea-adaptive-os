import test from 'node:test';
import assert from 'node:assert/strict';
import { storage } from '../storage.js';

test('storage save/load roundtrip works', () => {
  storage.save('x', { a: 1 });
  assert.deepEqual(storage.load('x'), { a: 1 });
});
