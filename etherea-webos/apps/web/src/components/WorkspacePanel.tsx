import { useMemo, useState } from 'react';
import { allowedFile, asFolder } from '../lib/commands';
import { deleteNode, renameNode, upsertNode, type WorkspaceFile } from '../lib/workspaceStore';

export function WorkspacePanel({
  files,
  onRefresh,
  compact = false,
}: {
  files: WorkspaceFile[];
  onRefresh: () => Promise<void>;
  compact?: boolean;
}) {
  const [openPath, setOpenPath] = useState('');
  const [draft, setDraft] = useState('');
  const [query, setQuery] = useState('');
  const [dirty, setDirty] = useState(false);

  const filtered = useMemo(() => files.filter((f) => f.path.toLowerCase().includes(query.toLowerCase())), [files, query]);

  async function open(path: string) {
    const node = files.find((f) => f.path === path);
    if (!node || node.type !== 'file') return;
    setOpenPath(path);
    setDraft(node.content);
    setDirty(false);
  }

  return (
    <section className={`card workspace ${compact ? 'compact' : ''}`}>
      <div className="workspace-left">
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search filenames" />
        <button
          onClick={async () => {
            const path = prompt('New file path (.md .txt .py ...)', 'notes.md')?.trim() ?? '';
            if (!path || !allowedFile(path)) return;
            await upsertNode({ path, content: '', updatedAt: Date.now(), type: 'file' });
            await onRefresh();
          }}
        >
          New file
        </button>
        <button
          onClick={async () => {
            const path = prompt('New folder path', 'notes')?.trim() ?? '';
            if (!path) return;
            await upsertNode(asFolder(path));
            await onRefresh();
          }}
        >
          New folder
        </button>
        {filtered.map((f) => (
          <div key={f.path} className="tree-node" onClick={() => open(f.path)}>
            {f.type === 'folder' ? '📁' : '📄'} {f.path}
          </div>
        ))}
      </div>
      {!compact && (
        <div className="workspace-main">
          <div className="tabs">{openPath || 'No file open'}</div>
          <textarea
            value={draft}
            onChange={(e) => {
              setDraft(e.target.value);
              setDirty(true);
            }}
            placeholder="Open a file to edit"
          />
          <div className="row">
            <button
              onClick={async () => {
                if (!openPath) return;
                await upsertNode({ path: openPath, content: draft, updatedAt: Date.now(), type: 'file' });
                setDirty(false);
                await onRefresh();
              }}
            >
              Save
            </button>
            <button
              onClick={async () => {
                if (!openPath) return;
                const next = prompt('Rename path', openPath)?.trim() ?? '';
                if (!next) return;
                await renameNode(openPath, next);
                setOpenPath(next);
                await onRefresh();
              }}
            >
              Rename
            </button>
            <button
              onClick={async () => {
                if (!openPath || !confirm(`Delete ${openPath}?`)) return;
                await deleteNode(openPath);
                setOpenPath('');
                setDraft('');
                setDirty(false);
                await onRefresh();
              }}
            >
              Delete
            </button>
          </div>
          <div className="statusbar">
            {openPath || 'none'} · {dirty ? 'dirty' : 'saved'}
          </div>
        </div>
      )}
    </section>
  );
}
