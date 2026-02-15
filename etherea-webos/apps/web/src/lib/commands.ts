import { deleteNode, listWorkspace, upsertNode, type WorkspaceFile } from './workspaceStore';
import { PRESET_ACCENTS, type ThemePreset, type ThemeSettings } from './theme';

export type CommandName =
  | 'create_file'
  | 'edit_file'
  | 'summarize_file'
  | 'list_files'
  | 'open_file'
  | 'set_theme'
  | 'set_mode'
  | 'help';

export type BrainCommand = {
  name: CommandName;
  args: Record<string, string | number | boolean | undefined>;
};

export async function executeCommand(
  command: BrainCommand,
  activeTheme: ThemeSettings,
  setTheme: (next: ThemeSettings) => void,
): Promise<string> {
  if (command.name === 'create_file' || command.name === 'edit_file') {
    const path = String(command.args.path ?? '').trim();
    if (!path) throw new Error('path is required');
    const content = String(command.args.content ?? '');
    await upsertNode({ path, content, updatedAt: Date.now(), type: 'file' });
    return `${command.name === 'create_file' ? 'Created' : 'Updated'} ${path}`;
  }
  if (command.name === 'summarize_file') {
    const path = String(command.args.path ?? '');
    const row = (await listWorkspace()).find((item) => item.path === path && item.type === 'file');
    if (!row) throw new Error(`File not found: ${path}`);
    const lines = row.content.split('\n').filter(Boolean);
    return `${path}: ${lines.length} lines, ${row.content.length} chars. Preview: ${row.content.slice(0, 120)}`;
  }
  if (command.name === 'list_files') {
    const depth = Number(command.args.depth ?? 3);
    const rows = (await listWorkspace())
      .filter((r) => r.path.split('/').length <= depth)
      .sort((a, b) => a.path.localeCompare(b.path));
    return rows.length ? rows.map((r) => `${r.type === 'folder' ? '📁' : '📄'} ${r.path}`).join('\n') : 'Workspace is empty.';
  }
  if (command.name === 'open_file') {
    return `Opening ${String(command.args.path ?? '')}`;
  }
  if (command.name === 'set_theme') {
    const preset = String(command.args.preset ?? 'nebula') as ThemePreset;
    const next = {
      ...activeTheme,
      preset,
      accent: String(command.args.accent ?? PRESET_ACCENTS[preset] ?? activeTheme.accent),
      glow: Number(command.args.glow ?? activeTheme.glow),
      rounded: Number(command.args.rounded ?? activeTheme.rounded),
      reducedMotion: Boolean(command.args.reducedMotion ?? activeTheme.reducedMotion),
    };
    setTheme(next);
    return `Theme set to ${preset}`;
  }
  if (command.name === 'set_mode') {
    const mode = String(command.args.mode ?? 'professional') as ThemeSettings['mode'];
    setTheme({ ...activeTheme, mode });
    return `Mode switched to ${mode}`;
  }
  if (command.name === 'help') {
    return 'Commands: create_file, edit_file, summarize_file, list_files, open_file, set_theme, set_mode, help';
  }
  return 'No action executed.';
}

export function allowedFile(path: string) {
  return /\.(md|txt|py|js|ts|java|cpp|c|json|yaml|yml|mmd|mermaid)$/i.test(path);
}

export function asFolder(path: string): WorkspaceFile {
  return { path, content: '', updatedAt: Date.now(), type: 'folder' };
}
