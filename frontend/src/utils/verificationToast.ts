import { Notify } from 'quasar';

export function showVerificationToastOnce(newStatus: string, message?: string): void {
  try {
    if (newStatus !== 'approved') return;

    const rawUser = localStorage.getItem('user');
    const user = rawUser ? JSON.parse(rawUser) : {};
    const identifier = user?.id ?? user?.email ?? 'unknown';
    const key = `verification_toast_shown_${identifier}`;

    if (localStorage.getItem(key) === 'true') return;

    Notify.create({
      type: 'positive',
      message: message || 'Congratulations! Your account has been verified and approved.',
      position: 'top',
      timeout: 5000,
      actions: [{ label: 'Dismiss', color: 'white' }],
    });

    localStorage.setItem(key, 'true');
  } catch {
    // Fallback: avoid repeated toasts within the same session
    const w = window as unknown as { __verification_toast_shown__?: boolean };
    if (w.__verification_toast_shown__) return;
    w.__verification_toast_shown__ = true;
  }
}