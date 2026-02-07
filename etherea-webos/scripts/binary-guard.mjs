import { execSync } from 'node:child_process';

const banned = ['.png', '.jpg', '.jpeg', '.webp', '.wav', '.mp3', '.ttf', '.otf', '.exe', '.apk', '.aab', '.zip'];
const files = execSync('git ls-files', { encoding: 'utf8' }).trim().split('\n').filter(Boolean);
const offenders = files.filter((f) => banned.some((ext) => f.toLowerCase().endsWith(ext)));
if (offenders.length) {
  console.error('Binary guard failed:\n' + offenders.join('\n'));
  process.exit(1);
}
console.log('Binary guard passed.');
