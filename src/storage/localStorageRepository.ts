import type { AccountRepository, ProgressRepository, UserProfile, StageCompletion } from './types';

const USER_KEY = 'noriUser';
const AUTH_KEY = 'noriAuth';
// Separate from the legacy ck.bN.sub.done keys the embedded game itself writes:
// those are device-wide (not scoped per account), so they can't answer "what has
// THIS kid completed" when a device is shared. This key adds that per-account view
// without touching the legacy keys the game's own hub/menu pages still read.
const PROGRESS_KEY = 'noriProgress';

function safeGet<T>(storage: Storage, key: string, fallback: T): T {
  try {
    const v = storage.getItem(key);
    return v == null ? fallback : JSON.parse(v);
  } catch {
    return fallback;
  }
}

function safeSet(storage: Storage, key: string, value: unknown): void {
  try {
    storage.setItem(key, JSON.stringify(value));
  } catch {
    // ignore (private browsing / quota)
  }
}

export const accountRepository: AccountRepository = {
  getCurrentUser() {
    return safeGet<UserProfile | null>(localStorage, USER_KEY, null);
  },
  saveUser(u) {
    safeSet(localStorage, USER_KEY, u);
  },
  signIn() {
    try {
      sessionStorage.setItem(AUTH_KEY, '1');
    } catch {
      // ignore
    }
  },
  signOut() {
    try {
      sessionStorage.removeItem(AUTH_KEY);
    } catch {
      // ignore
    }
  },
  isSignedIn() {
    try {
      return sessionStorage.getItem(AUTH_KEY) === '1';
    } catch {
      return false;
    }
  },
};

type ProgressStore = Record<string, StageCompletion[]>;

export const progressRepository: ProgressRepository = {
  getCompletions(email) {
    const store = safeGet<ProgressStore>(localStorage, PROGRESS_KEY, {});
    return store[email] ?? [];
  },
  recordCompletion(email, theme, stage) {
    const store = safeGet<ProgressStore>(localStorage, PROGRESS_KEY, {});
    const list = store[email] ?? [];
    if (!list.some((c) => c.theme === theme && c.stage === stage)) {
      list.push({ theme, stage, completedAt: Date.now() });
      store[email] = list;
      safeSet(localStorage, PROGRESS_KEY, store);
    }
  },
};
