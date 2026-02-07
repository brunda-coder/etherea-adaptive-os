export interface StorageAdapter {
  getItem(key: string): Promise<string | null>;
  setItem(key: string, value: string): Promise<void>;
}

export class InMemoryStorage implements StorageAdapter {
  private readonly memory = new Map<string, string>();

  async getItem(key: string): Promise<string | null> {
    return this.memory.get(key) ?? null;
  }

  async setItem(key: string, value: string): Promise<void> {
    this.memory.set(key, value);
  }
}

export async function saveJson<T>(adapter: StorageAdapter, key: string, value: T): Promise<void> {
  await adapter.setItem(key, JSON.stringify(value));
}

export async function loadJson<T>(adapter: StorageAdapter, key: string): Promise<T | null> {
  const raw = await adapter.getItem(key);
  return raw ? (JSON.parse(raw) as T) : null;
}
