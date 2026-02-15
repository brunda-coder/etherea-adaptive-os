export type WorkspaceFile = { path: string; content: string; updatedAt: number; type: 'file' | 'folder' };

const DB_NAME = 'etherea-workspace';
const STORE = 'nodes';
const LS_KEY = 'etherea.workspace.v1';

function supportsIDB() {
  return typeof window !== 'undefined' && 'indexedDB' in window;
}

async function withDb<T>(fn: (db: IDBDatabase) => Promise<T>): Promise<T> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(STORE)) db.createObjectStore(STORE, { keyPath: 'path' });
    };
    req.onsuccess = async () => {
      try {
        resolve(await fn(req.result));
      } catch (error) {
        reject(error);
      }
    };
    req.onerror = () => reject(req.error);
  });
}

function readLs(): WorkspaceFile[] {
  try {
    return JSON.parse(localStorage.getItem(LS_KEY) ?? '[]') as WorkspaceFile[];
  } catch {
    return [];
  }
}

function writeLs(rows: WorkspaceFile[]) {
  localStorage.setItem(LS_KEY, JSON.stringify(rows));
}

export async function listWorkspace(): Promise<WorkspaceFile[]> {
  if (!supportsIDB()) return readLs();
  return withDb(
    (db) =>
      new Promise((resolve) => {
        const tx = db.transaction(STORE, 'readonly');
        const req = tx.objectStore(STORE).getAll();
        req.onsuccess = () => resolve((req.result as WorkspaceFile[]) ?? []);
        req.onerror = () => resolve([]);
      }),
  );
}

export async function upsertNode(node: WorkspaceFile) {
  if (!supportsIDB()) {
    const rows = readLs().filter((r) => r.path !== node.path);
    rows.push(node);
    writeLs(rows);
    return;
  }
  await withDb(
    (db) =>
      new Promise<void>((resolve, reject) => {
        const tx = db.transaction(STORE, 'readwrite');
        tx.objectStore(STORE).put(node);
        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
      }),
  );
}

export async function deleteNode(path: string) {
  if (!supportsIDB()) {
    writeLs(readLs().filter((r) => !r.path.startsWith(path)));
    return;
  }
  const rows = await listWorkspace();
  const toDelete = rows.filter((r) => r.path === path || r.path.startsWith(`${path}/`));
  await withDb(
    (db) =>
      new Promise<void>((resolve, reject) => {
        const tx = db.transaction(STORE, 'readwrite');
        toDelete.forEach((node) => tx.objectStore(STORE).delete(node.path));
        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
      }),
  );
}

export async function renameNode(path: string, nextPath: string) {
  const rows = await listWorkspace();
  const matched = rows.filter((r) => r.path === path || r.path.startsWith(`${path}/`));
  for (const row of matched) {
    await deleteNode(row.path);
    await upsertNode({ ...row, path: row.path.replace(path, nextPath) });
  }
}
