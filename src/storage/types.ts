export interface UserProfile {
  email: string;
  name: string;
  age: number | '';
  avatar: string;
  interests: number[];
  remember: boolean;
  done: boolean;
}

export interface StageCompletion {
  theme: string;
  stage: string;
  completedAt: number;
}

export interface AccountRepository {
  getCurrentUser(): UserProfile | null;
  saveUser(u: UserProfile): void;
  signIn(): void;
  signOut(): void;
  isSignedIn(): boolean;
}

export interface ProgressRepository {
  getCompletions(email: string): StageCompletion[];
  recordCompletion(email: string, theme: string, stage: string): void;
}
