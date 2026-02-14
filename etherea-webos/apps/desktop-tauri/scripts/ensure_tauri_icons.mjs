#!/usr/bin/env node
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';

const svgPath = 'src-tauri/assets/icon.svg';
const iconsDir = 'src-tauri/icons';
const icoPath = `${iconsDir}/icon.ico`;

const fallbackSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="112" fill="#111827"/>
  <path d="M120 120h272v72H264v64h120v72H264v64h128v72H120z" fill="#a78bfa"/>
</svg>\n`;

if (!existsSync(svgPath)) {
  console.log(`[ensure_tauri_icons] ${svgPath} missing. Creating default SVG...`);
  mkdirSync('src-tauri/assets', { recursive: true });
  writeFileSync(svgPath, fallbackSvg, 'utf8');
}

mkdirSync(iconsDir, { recursive: true });

if (!existsSync(icoPath)) {
  console.log('[ensure_tauri_icons] icon.ico missing. Running `npx --yes tauri icon "src-tauri/assets/icon.svg"`...');
  const result = spawnSync('npx', ['--yes', 'tauri', 'icon', svgPath], {
    stdio: 'inherit',
    shell: process.platform === 'win32'
  });

  if (result.status !== 0) {
    console.error(`[ensure_tauri_icons] Failed to generate Tauri icons (exit ${result.status ?? 'unknown'}).`);
    process.exit(result.status ?? 1);
  }
}

if (!existsSync(icoPath)) {
  console.error(`[ensure_tauri_icons] Expected ${icoPath} after generation, but it does not exist.`);
  process.exit(1);
}

console.log('[ensure_tauri_icons] Tauri icon assets are ready.');
