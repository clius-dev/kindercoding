import { useEffect, useState } from 'react';
import { accountRepository } from '../storage/localStorageRepository';
import type { UserProfile } from '../storage/types';
import { GAME_BASE } from '../gameBase';

/* Ported from Coding/B_0_main/A-1_login.html + A_account.js — same markup/classes so the
   linked DESIGN.css/RESPONSIVE.css/A_account.css (from public/game/) render it identically. */

const AVATARS = [
  { id: 'boy', src: `${GAME_BASE}img_svg/avatar/avatar_boy.svg` },
  { id: 'girl', src: `${GAME_BASE}img_svg/avatar/avatar_girl.svg` },
  { id: 'kid', src: `${GAME_BASE}img_svg/avatar/avatar_kid.svg` },
  { id: 'monster', src: `${GAME_BASE}img_svg/avatar/avatar_monster.svg` },
  { id: 'curly', src: `${GAME_BASE}img_svg/avatar/avatar_curly.png` },
  { id: 'bun', src: `${GAME_BASE}img_svg/avatar/avatar_bun.png` },
];

const THEMES: Record<'en' | 'ko', string[]> = {
  en: ['School & Friends', 'Spring', 'Plants & Animals', 'Me & My Family', 'My Town', 'Health & Nature', 'Summer', 'Transportation', 'Autumn & Fruits', 'Environment', 'Winter & Play', 'Tools We Use'],
  ko: ['어린이집과 친구', '봄', '동식물과 자연', '나와 가족', '우리 동네', '건강과 자연', '여름', '교통기관', '가을과 열매', '환경과 생활', '겨울과 놀이', '생활과 도구'],
};

const D = {
  en: { loginTtl: 'Ready to play?', signupTtl: 'Create your account', email: 'Email or ID', pw: 'Password', remember: 'Keep me logged in', forgot: 'Forgot ID / password?',
    login: 'Log in', signup: 'Sign up', or: 'or', newHere: 'New here?', haveAcc: 'Already have an account?', loginLink: 'Log in', soon: 'Coming soon!',
    tos: 'Terms of Use', privacy: 'Privacy Policy',
    errEmail: 'Please enter your email or ID.', errPw: 'Password must be at least 4 characters.',
    set1Ttl: 'Set up your profile', set1Sub: 'Enter a name and choose a character and age.', name: 'Name', namePh: 'Name or nickname', avatar: 'Character', age: 'Age', next: 'Next', prev: 'Back',
    errName: 'Please enter a name.', errAge: 'Please choose an age.', set2Ttl: 'Choose your interests', set2Sub: 'Select the topics you are interested in.', start: 'Get started', errTheme: 'Pick at least one theme.',
    yr: (n: number) => String(n) },
  ko: { loginTtl: '오늘도 함께 놀아요!', signupTtl: '계정 만들기', email: '이메일 또는 아이디', pw: '비밀번호', remember: '로그인 유지', forgot: '아이디 · 비밀번호 찾기',
    login: '로그인', signup: '회원가입', or: '또는', newHere: '처음이신가요?', haveAcc: '이미 계정이 있으신가요?', loginLink: '로그인', soon: '준비 중이에요!',
    tos: '이용약관', privacy: '개인정보처리방침',
    errEmail: '이메일 또는 아이디를 입력해 주세요.', errPw: '비밀번호는 4자 이상이어야 합니다.',
    set1Ttl: '프로필 설정', set1Sub: '이름을 입력하고 캐릭터와 나이를 선택해 주세요.', name: '이름', namePh: '이름 또는 별명', avatar: '캐릭터', age: '나이', next: '다음', prev: '이전',
    errName: '이름을 입력해 주세요.', errAge: '나이를 선택해 주세요.', set2Ttl: '관심 주제 선택', set2Sub: '관심 있는 주제를 선택해 주세요.', start: '시작하기', errTheme: '주제를 하나 이상 선택해 주세요.',
    yr: (n: number) => `${n}살` },
};

function useGameStylesheets() {
  useEffect(() => {
    const hrefs = [
      'https://cdn.jsdelivr.net/gh/fonts-archive/Paperlogy/Paperlogy.css',
      `${GAME_BASE}DESIGN.css`,
      `${GAME_BASE}RESPONSIVE.css`,
      `${GAME_BASE}B_0_main/A_account.css`,
    ];
    const links = hrefs.map((href) => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      document.head.appendChild(link);
      return link;
    });
    const style = document.createElement('style');
    style.textContent = `:root,body{--bg-img:url("${GAME_BASE}img_png/main/main-stage-bg-login-wide-v1.webp")}
body::after{display:none}body::before{filter:saturate(.93)}
.grid-age{display:grid!important;grid-template-columns:repeat(7,1fr);gap:calc(14 * var(--u));justify-content:stretch!important}
.grid-age .ac-chip{width:100%;min-width:0;padding:0}`;
    document.head.appendChild(style);
    return () => {
      links.forEach((l) => l.remove());
      style.remove();
    };
  }, []);
}

type View = 'login' | 'set1' | 'set2';

export default function LoginPage({ onLoggedIn }: { onLoggedIn: (u: UserProfile) => void }) {
  useGameStylesheets();

  const [lang, setLang] = useState<'en' | 'ko'>(() => (localStorage.getItem('noriLang') === 'ko' ? 'ko' : 'en'));
  const [mode, setMode] = useState<'login' | 'signup'>('login');
  const [view, setView] = useState<View>('login');

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(true);
  const [loginError, setLoginError] = useState('');

  const [name, setName] = useState('');
  const [avatar, setAvatar] = useState('boy');
  const [age, setAge] = useState<number | ''>('');
  const [err1, setErr1] = useState('');

  const [interests, setInterests] = useState<number[]>([]);
  const [err2, setErr2] = useState('');

  const t = D[lang];

  function toggleLang() {
    const next = lang === 'en' ? 'ko' : 'en';
    setLang(next);
    try {
      localStorage.setItem('noriLang', next);
    } catch {
      // ignore
    }
  }

  function handleLoginSubmit(e: React.FormEvent) {
    e.preventDefault();
    const em = email.trim();
    setLoginError('');
    if (!em) return setLoginError(t.errEmail);
    if (password.length < 4) return setLoginError(t.errPw);

    let u = accountRepository.getCurrentUser();
    // mock: password is neither stored nor verified, matching the original prototype
    if (!u || u.email !== em) u = { email: em, name: '', age: '', avatar: 'boy', interests: [], remember, done: false };
    u.remember = remember;
    accountRepository.saveUser(u);

    if (u.done) {
      accountRepository.signIn();
      onLoggedIn(u);
      return;
    }
    setName(u.name || '');
    setAvatar(u.avatar || 'boy');
    setAge(u.age || '');
    setView('set1');
  }

  function handleNext1() {
    const nm = name.trim();
    if (!nm) return setErr1(t.errName);
    if (!age) return setErr1(t.errAge);
    setErr1('');
    setView('set2');
  }

  function handleDone() {
    if (!interests.length) return setErr2(t.errTheme);
    const u: UserProfile = {
      ...(accountRepository.getCurrentUser() ?? { email: email.trim(), remember, done: false }),
      name: name.trim(),
      age: Number(age),
      avatar,
      interests,
      done: true,
    };
    accountRepository.saveUser(u);
    accountRepository.signIn();
    onLoggedIn(u);
  }

  function toggleInterest(i: number) {
    setErr2('');
    setInterests((prev) => (prev.includes(i) ? prev.filter((x) => x !== i) : [...prev, i]));
  }

  return (
    <main className="stage theme-paper" id="app">
      <div className="pp-edge-tr">
        <button className="pp-ibtn pp-ibtn--lang" type="button" aria-label="Change language" onClick={toggleLang}>
          <span className="lg">
            <b className={lang === 'en' ? 'on' : 'off'}>A</b>
            <i className={lang === 'ko' ? 'on' : 'off'}>한</i>
          </span>
        </button>
      </div>

      {view === 'login' && (
        <section className="pp-sheet ac-sheet" style={{ width: 'calc(1160 * var(--u))', height: 'calc(1040 * var(--u))', gap: 'calc(14 * var(--u))', justifyContent: 'center' }}>
          <h1 className="ac-ttl" style={{ marginBottom: 'calc(14 * var(--u))' }}>{mode === 'login' ? t.loginTtl : t.signupTtl}</h1>
          <form onSubmit={handleLoginSubmit} style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'calc(14 * var(--u))' }} noValidate>
            <input className={`ac-field${loginError && !email.trim() ? ' is-bad' : ''}`} type="text" inputMode="email" autoComplete="username" placeholder={t.email} aria-label="Email or ID" value={email} onChange={(e) => setEmail(e.target.value)} />
            <input className={`ac-field${loginError && email.trim() && password.length < 4 ? ' is-bad' : ''}`} type="password" autoComplete="current-password" placeholder={t.pw} aria-label="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
            <p className="ac-err" role="alert">{loginError}</p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
              <label className="ac-switch">
                <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
                <i /><span>{t.remember}</span>
              </label>
              <button className="ac-link" type="button" onClick={() => alert(t.soon)}>{t.forgot}</button>
            </div>
            <button className="btn-bar ac-cta" type="submit"><span>{mode === 'login' ? t.login : t.signup}</span></button>
          </form>
          <div className="ac-or" style={{ margin: 'calc(14 * var(--u)) 0 calc(10 * var(--u))' }}><span>{t.or}</span></div>
          <div style={{ display: 'flex', gap: 'calc(20 * var(--u))' }}>
            <button className="ac-btn2" type="button" onClick={() => alert(t.soon)}>Apple</button>
            <button className="ac-btn2" type="button" onClick={() => alert(t.soon)}>Google</button>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'calc(10 * var(--u))', fontSize: 'calc(28 * var(--u))', fontWeight: 750 }}>
            <span>{mode === 'login' ? t.newHere : t.haveAcc}</span>
            <button className="ac-link" type="button" onClick={() => { setMode(mode === 'login' ? 'signup' : 'login'); setLoginError(''); }}>{mode === 'login' ? t.signup : t.loginLink}</button>
          </div>
          <p className="ac-note" style={{ textAlign: 'center', margin: 0 }}>
            <a href="#" style={{ color: 'inherit', textDecoration: 'underline' }}>{t.tos}</a> <span aria-hidden="true">|</span>{' '}
            <a href="#" style={{ color: 'inherit', textDecoration: 'underline' }}>{t.privacy}</a>
          </p>
        </section>
      )}

      {view === 'set1' && (
        <section className="pp-sheet ac-sheet" style={{ width: 'calc(1160 * var(--u))', height: 'calc(1040 * var(--u))', gap: 'calc(28 * var(--u))', justifyContent: 'center' }}>
          <h1 className="ac-ttl">{t.set1Ttl}</h1>
          <p className="ac-sub" style={{ margin: '0 0 calc(8 * var(--u))' }}>{t.set1Sub}</p>
          <div style={{ width: '100%' }}>
            <span className="ac-lbl">{t.name}</span>
            <input className="ac-field" type="text" maxLength={12} autoComplete="off" placeholder={t.namePh} aria-label="Name" value={name} onChange={(e) => { setName(e.target.value); setErr1(''); }} />
          </div>
          <div style={{ width: '100%' }}>
            <span className="ac-lbl">{t.avatar}</span>
            <div className="ac-avs" style={{ display: 'grid', gridTemplateColumns: 'repeat(6,1fr)', justifyItems: 'center' }}>
              {AVATARS.map((a) => (
                <button key={a.id} type="button" className="ac-avb" aria-pressed={avatar === a.id} aria-label={a.id} onClick={() => setAvatar(a.id)}>
                  <img src={a.src} alt="" />
                </button>
              ))}
            </div>
          </div>
          <div style={{ width: '100%' }}>
            <span className="ac-lbl">{t.age}</span>
            <div className="ac-chips grid-age">
              {Array.from({ length: 7 }, (_, i) => i + 3).map((n) => (
                <button key={n} type="button" className="ac-chip" aria-pressed={age === n} onClick={() => { setAge(n); setErr1(''); }}>{t.yr(n)}</button>
              ))}
            </div>
          </div>
          <p className="ac-err" role="alert" style={{ textAlign: 'center', margin: 0 }}>{err1}</p>
          <button className="btn-bar ac-cta" type="button" onClick={handleNext1}><span>{t.next}</span></button>
        </section>
      )}

      {view === 'set2' && (
        <section className="pp-sheet ac-sheet" style={{ width: 'calc(1160 * var(--u))', height: 'calc(1040 * var(--u))', gap: 'calc(28 * var(--u))', justifyContent: 'center' }}>
          <h1 className="ac-ttl">{t.set2Ttl}</h1>
          <p className="ac-sub" style={{ margin: '0 0 calc(8 * var(--u))' }}>{t.set2Sub}</p>
          <div className="ac-chips" style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', width: '100%', gap: 'calc(16 * var(--u))' }}>
            {THEMES[lang].map((label, i) => (
              <button key={i} type="button" className="ac-chip" aria-pressed={interests.includes(i)} onClick={() => toggleInterest(i)}>{label}</button>
            ))}
          </div>
          <p className="ac-err" role="alert" style={{ textAlign: 'center', margin: 0 }}>{err2}</p>
          <div style={{ display: 'flex', gap: 'calc(24 * var(--u))', alignItems: 'center' }}>
            <button className="btn-bar ac-cta ac-cta--s ac-cta--exit" type="button" style={{ ['--bb-w' as string]: 230 }} onClick={() => setView('set1')}><span>{t.prev}</span></button>
            <button className="btn-bar ac-cta ac-cta--s" type="button" style={{ ['--bb-w' as string]: 420 }} onClick={handleDone}><span>{t.start}</span></button>
          </div>
        </section>
      )}
    </main>
  );
}
