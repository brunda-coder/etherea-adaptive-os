import { useCallback, useMemo, useState } from 'react';

export type ToastType = 'success' | 'error' | 'info';

export type ToastItem = {
  id: number;
  type: ToastType;
  message: string;
};

export function useToast(timeoutMs = 2600) {
  const [toast, setToast] = useState<ToastItem | null>(null);

  const pushToast = useCallback((type: ToastType, message: string) => {
    const id = Date.now();
    setToast({ id, type, message });
    window.setTimeout(() => {
      setToast((current) => (current?.id === id ? null : current));
    }, timeoutMs);
  }, [timeoutMs]);

  return useMemo(
    () => ({
      toast,
      showInfo: (message: string) => pushToast('info', message),
      showSuccess: (message: string) => pushToast('success', message),
      showError: (message: string) => pushToast('error', message),
      clearToast: () => setToast(null),
    }),
    [pushToast, toast],
  );
}
