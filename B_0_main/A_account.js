/* A_account.js — 로그인 · 내 정보 · 부모 관리 공통 (저장·언어·토스트·출석)
   저장소: localStorage(이 기기 전용 프로토타입). 서버·실제 인증은 없음.
   키: noriUser {email,name,age,avatar,interests[],remember,done} · noriLang('en'|'ko') · noriAttend [YYYY-MM-DD] · noriLimit(분) · noriBreak · noriBgm('on'|'off') */
(function(){
  const S = {
    get(k, d){ try{ const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v) }catch(e){ return d } },
    set(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)) }catch(e){} },
    del(k){ try{ localStorage.removeItem(k) }catch(e){} }
  };
  const A = window.AC = {S};

  /* 서브메인 버스 그림의 4명(주황머리·단발머리·상투머리 · 보라 고양이) — 팔을 뺀 얼굴+몸통만, 얼굴이 원 중앙에 오도록 자른 SVG */
  A.AVATARS = [
    {id:'boy', src:'../img_svg/avatar/avatar_boy.svg'},
    {id:'girl', src:'../img_svg/avatar/avatar_girl.svg'},
    {id:'kid', src:'../img_svg/avatar/avatar_kid.svg'},
    {id:'monster', src:'../img_svg/avatar/avatar_monster.svg'},
    {id:'curly', src:'../img_svg/avatar/avatar_curly.png'},
    {id:'bun', src:'../img_svg/avatar/avatar_bun.png'}
  ];
  A.avatarSrc = id => (A.AVATARS.find(a => a.id === id) || A.AVATARS[0]).src;
  A.THEMES = {
    en:['School & Friends','Spring','Plants & Animals','Me & My Family','My Town','Health & Nature','Summer','Transportation','Autumn & Fruits','Environment','Winter & Play','Tools We Use'],
    ko:['어린이집과 친구','봄','동식물과 자연','나와 가족','우리 동네','건강과 자연','여름','교통기관','가을과 열매','환경과 생활','겨울과 놀이','생활과 도구']
  };

  /* 언어 — 메인과 같은 키(noriLang). 기본 English */
  /* main.html 과 같은 형식: 순수 문자열('ko'|'en') — JSON 아님 */
  A.lang = (() => { try{ return localStorage.getItem('noriLang') === 'ko' ? 'ko' : 'en' }catch(e){ return 'en' } })();
  A.setLang = l => { A.lang = l; try{ localStorage.setItem('noriLang', l) }catch(e){} };

  /* 사용자 */
  A.user = () => S.get('noriUser', null);
  A.saveUser = u => S.set('noriUser', u);

  /* 출석 — 이 화면들에 들어온 날을 기록 */
  const ymd = d => d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
  A.touchAttend = () => { const a = S.get('noriAttend', []); const t = ymd(new Date()); if(a.indexOf(t) < 0){ a.push(t); S.set('noriAttend', a.slice(-120)) } return a.length };
  A.attendDays = () => S.get('noriAttend', []).length;
  A.week = () => { const a = S.get('noriAttend', []); const out = []; const now = new Date();
    for(let i = 6; i >= 0; i--){ const d = new Date(now); d.setDate(now.getDate() - i); out.push({dow:d.getDay(), on:a.indexOf(ymd(d)) >= 0}) } return out };

  /* 완료 스테이지 — 서브메인이 기록하는 키(ck.b?.sub.done) */
  const cnt = v => Array.isArray(v) ? v.length : (v && typeof v === 'object') ? Object.keys(v).filter(k => v[k]).length : (typeof v === 'number' ? v : 0);
  A.stages = () => ({b1:cnt(S.get('ck.b1.sub.done', 0)), b2:cnt(S.get('ck.b2.sub.done', 0)), b3:cnt(S.get('ck.b3.sub.done', 0))});
  A.stagesTotal = () => { const s = A.stages(); return s.b1 + s.b2 + s.b3 };

  /* 토스트 */
  let tt = 0;
  A.toast = (msg) => { let el = document.getElementById('toast'); if(!el){ el = document.createElement('div'); el.id = 'toast'; el.className = 'toast'; document.body.appendChild(el) }
    el.textContent = msg; el.classList.add('is-on'); clearTimeout(tt); tt = setTimeout(() => el.classList.remove('is-on'), 1800) };

  /* 이번 실행(탭) 로그인 표시 — main.html 입구 검사와 같은 키(noriAuth) */
  A.signIn = () => { try{ sessionStorage.setItem('noriAuth','1') }catch(e){} };
  A.signOut = () => { try{ sessionStorage.removeItem('noriAuth') }catch(e){} };

  /* 이동 */
  A.go = url => { location.href = url };

  /* 언어 토글 버튼(#lang) 공통 배선 */
  A.bindLang = (apply) => { const b = document.getElementById('lang'); if(!b) return;
    const paint = () => { b.querySelector('b').className = A.lang === 'en' ? 'on' : 'off'; b.querySelector('i').className = A.lang === 'ko' ? 'on' : 'off'; document.documentElement.lang = A.lang };
    b.addEventListener('click', () => { A.setLang(A.lang === 'en' ? 'ko' : 'en'); paint(); apply() });
    paint(); };

  /* data-i18n 일괄 치환: dict[lang][key] */
  A.applyI18n = (dict) => { const d = dict[A.lang]; document.querySelectorAll('[data-i]').forEach(el => { const v = d[el.dataset.i]; if(v != null) el.textContent = v });
    document.querySelectorAll('[data-ph]').forEach(el => { const v = d[el.dataset.ph]; if(v != null) el.placeholder = v });
    document.querySelectorAll('[data-al]').forEach(el => { const v = d[el.dataset.al]; if(v != null) el.setAttribute('aria-label', v) }); };

  /* 칩 단일/다중 선택 헬퍼 */
  A.chipGroup = (root, {multi=false, onChange}={}) => {
    root.addEventListener('click', e => { const c = e.target.closest('[aria-pressed]'); if(!c || !root.contains(c)) return;
      if(multi) c.setAttribute('aria-pressed', c.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
      else { root.querySelectorAll('[aria-pressed]').forEach(x => x.setAttribute('aria-pressed', 'false')); c.setAttribute('aria-pressed', 'true') }
      onChange && onChange(A.chipValues(root)) });
  };
  A.chipValues = root => [...root.querySelectorAll('[aria-pressed="true"]')].map(c => c.dataset.v);
  A.setChips = (root, vals) => { const set = new Set((Array.isArray(vals) ? vals : [vals]).map(String)); root.querySelectorAll('[aria-pressed]').forEach(c => c.setAttribute('aria-pressed', set.has(String(c.dataset.v)) ? 'true' : 'false')) };
})();
