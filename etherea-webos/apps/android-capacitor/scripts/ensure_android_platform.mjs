#!/usr/bin/env node
import { existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';

const androidDir = 'android';

if (existsSync(androidDir)) {
  console.log('[ensure_android_platform] android/ already exists. Skipping `cap add android`.');
  process.exit(0);
}

console.log('[ensure_android_platform] android/ missing. Running `npx --yes cap add android`...');
const result = spawnSync('npx', ['--yes', 'cap', 'add', 'android'], {
  stdio: 'inherit',
  shell: process.platform === 'win32'
});

if (result.status !== 0) {
  console.error(`[ensure_android_platform] Failed to add Android platform (exit ${result.status ?? 'unknown'}).`);
  process.exit(result.status ?? 1);
}

if (!existsSync(androidDir)) {
  console.error('[ensure_android_platform] `cap add android` completed but android/ is still missing.');
  process.exit(1);
}

console.log('[ensure_android_platform] android/ platform is ready.');
