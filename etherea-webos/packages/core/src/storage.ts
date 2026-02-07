const memory = new Map<string, string>();

export const storage = {
  save<T>(key: string, value: T): void {
    memory.set(key, JSON.stringify(value));
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(key, JSON.stringify(value));
    }
  },
  load<T>(key: string): T | null {
    if (typeof localStorage !== 'undefined') {
      const raw = localStorage.getItem(key);
      return raw ? (JSON.parse(raw) as T) : null;
    }
    const raw = memory.get(key);
    return raw ? (JSON.parse(raw) as T) : null;
  },
  clear(): void {
    memory.clear();
    if (typeof localStorage !== 'undefined') {
      localStorage.clear();
    }
  }
};
