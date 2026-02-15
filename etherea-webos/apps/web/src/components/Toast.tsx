export function Toast({ message, type = 'info' }: { message: string | null; type?: 'success' | 'error' | 'info' }) {
  if (!message) return null;
  return <div className={`toast ${type}`}>{message}</div>;
}
