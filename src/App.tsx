import { useState } from 'react';
import LoginPage from './routes/LoginPage';
import GameFrame from './components/GameFrame';
import { accountRepository } from './storage/localStorageRepository';
import type { UserProfile } from './storage/types';

type Screen = 'login' | 'game';

function initialState(): { screen: Screen; user: UserProfile | null } {
  const user = accountRepository.getCurrentUser();
  if (accountRepository.isSignedIn() && user) return { screen: 'game', user };
  // matches the original A-1_login.html: a remembered, completed profile skips login
  if (user?.remember && user.done) {
    accountRepository.signIn();
    return { screen: 'game', user };
  }
  return { screen: 'login', user };
}

function App() {
  const [{ screen, user }, setState] = useState(initialState);

  if (screen === 'game' && user) {
    return <GameFrame email={user.email} />;
  }
  return <LoginPage onLoggedIn={(u) => setState({ screen: 'game', user: u })} />;
}

export default App;
