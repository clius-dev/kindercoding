# Plan: 기존 HTML 게임 → React(iframe) 포팅

## Context
디자이너가 `E:\01_Work\06_KinderCoding\03-Work\Coding`(SVN, 수시 변경)에 작업한 HTML 키즈 코딩 게임을, `H:\test`에 새로 만들 Vite+TypeScript React 앱에서 `<iframe>`으로 그대로 보여주면서, 계정/로그인과 스테이지 완료·점수 기록은 React가 로컬에 관리하도록 포팅한다. 최종 결과물은 기존 GitHub 저장소 [clius-dev/kindercoding](https://github.com/clius-dev/kindercoding)(Public)에 올리고, 현재 그 저장소의 GitHub Pages가 서빙 중인 "원본 HTML 그대로 미러" 배포를 새 React 앱으로 교체한다(사용자 확정 사항). `H:\test\intent.md`에 전체 배경이 정리되어 있다.

### 조사로 확인된 핵심 사실
- **탐색 방식**: 전부 멀티페이지 이동(`location.href`), SPA 아님. 대부분 `loading.html?to=...`를 경유. 이동 대상 경로가 JS 문자열 배열(`FILES`, `NODES[].href` 등)로 동적 생성되는 경우가 많아, 단순 정적 링크 파싱만으론 부족함.
- **계정 로직** (`B_0_main/A_account.js`): 순수 localStorage 목업. 키 `noriUser` = `{email,name,age,avatar,interests,remember,done}`. **비밀번호는 저장·검증 안 함** (원본 주석으로 명시). 그 외 `noriLang`, `noriAttend`, `sessionStorage.noriAuth`, 진행도 조회용 `ck.bN.sub.done`(스테이지별 완료 배열).
- **스테이지 완료 감지**: 각 스테이지 HTML 끝에 붙은 "MAP-PROGRESS" 스니펫이 `#win` 오버레이에 `.on` 클래스가 붙는 걸 `MutationObserver`로 감지해 `localStorage`에 기록. **postMessage/CustomEvent는 전혀 없음** → 직접 주입 필요.
- **에셋 경로**: 참조하는 파일 기준 상대경로(`../`)로 일관. 폴더 구조를 그대로 유지해서 복사하면 경로 재작성 없이 동작.
- **소스 규모**: 1.6GB/2,743파일. `_old/`, `공유/`, `비주얼컨셉안/`, `이전작업/`과 다수의 미참조 에셋 버전(`-v1`~`-v29` 등)이 죽은 파일 ? 링크 추적(BFS) 방식으로 자동 제외됨.
- **GitHub 저장소**: `main` 루트가 원본 그대로 미러된 정적 사이트, GitHub Pages가 그 루트를 직접 서빙 중. React/Vite 프로젝트 없음, 브랜치는 `main` 하나뿐. 커밋 이력은 "전체 삭제→전체 재복사" 동기화 패턴.

### 설계상 가정 (명시적으로 선택한 기본값, 이상하면 바로 알려주세요)
1. **iframe 범위**: React는 로그인 화면 하나만 직접 구현/렌더링하고, 로그인 이후(`main.html`부터 메뉴·테마 허브·스테이지까지 전부)는 기존 설계 그대로 **하나의 iframe**에 담는다. 메뉴/허브까지 React로 새로 만들지 않는다 ? "디자인·조작 동일"을 가장 안전하게 지키는 방법이고, 작업량도 크게 줄어든다.
2. **완료 표시**: React는 완료 이벤트를 받아 로컬 DB에 "조용히" 기록만 한다. 화면에 보이는 완료 표시는 게임 안에 이미 있는 `#win` 오버레이가 그대로 담당 (React가 별도 팝업/토스트를 덧씌우지 않음).
3. `A_account.js`의 `A.stages()`가 원래 B-1~B-3까지만 진행도를 집계하는 건 원본의 누락처럼 보여서, React 포팅판에서는 B-1~B-6 전체로 일반화한다.

---

## 1. 파일 동기화 스크립트 (`scripts/sync-game.mjs`)
- Node.js(ESM) 스크립트로 저장소에 포함, `node scripts/sync-game.mjs [--source <path>] [--dry-run]`로 재실행 가능해야 함(디자이너 작업물이 수시로 바뀌므로).
- `B_0_main/main.html`, `loading.html`, 공유 CSS/JS(`DESIGN.css`, `RESPONSIVE.css/js`, `EXIT_CONFIRM.js`)를 시작점으로 BFS:
  - `.html`은 정적 속성(`href`/`src`) + 원본 텍스트 정규식 스캔(`url(...)`, `new Audio(...)`, 상대경로처럼 보이는 문자열 리터럴, 배열+문자열 접합 패턴)으로 참조를 추출.
  - `.css`/`.js`도 동일한 문자열 리터럴 정규식으로 스캔.
  - 참조 경로는 "참조하는 파일 기준" 상대경로로 resolve.
  - `_old/`, `공유/`, `비주얼컨셉안/`, `이전작업/` 경로는 어떤 깊이에서든 제외.
  - 확신 없는 후보 경로는 버리지 않고 `scripts/sync-report.json`의 "unresolved" 목록에 기록 (수동 점검용).
- 매 실행마다 `public/game/` 전체를 삭제 후 BFS로 찾은 파일만 다시 복사(디자이너 쪽 파일명 변경/버전 교체에 안전하게 대응).
- `public/game/`은 스크립트가 생성하는 산출물이므로 사람이 직접 수정하지 않는다는 걸 README/마커 파일로 명시.

## 2. postMessage 훅 주입 (동일 스크립트 내)
- 각 스테이지 HTML에 이미 존재하는 `MAP-PROGRESS` 스니펫을 정규식으로 찾아 `stage id`/`localStorage 키`를 그대로 추출 (하드코딩 매핑 테이블 불필요, 디자이너가 id를 바꿔도 자동 추적됨).
- 매칭되면 바로 뒤에 두 번째 `<script>`를 삽입: 동일한 `#win.on` 감지 시 `window.parent.postMessage({source:'kindercoding-game', type:'stageComplete', theme, stage, key, ts}, '*')` 호출.
- 로그인/메뉴/허브 페이지처럼 이 스니펫이 없는 파일은 자동으로 건너뜀.
- SVN 원본은 절대 수정하지 않음 ? 복사본에만 주입.

## 3. React 앱 구조 (Vite + TS)
```
H:\test
  scripts/sync-game.mjs
  public/game/              ← 동기화 스크립트 산출물
  src/
    App.tsx                 ← 'login' | 'game' 상태만 있는 단순 전환 (라우터 불필요)
    routes/LoginPage.tsx     ← A-1_login.html + A_account.js 포팅
    components/GameFrame.tsx ← <iframe src="/game/B_0_main/main.html"> + message 리스너
    storage/types.ts         ← AccountRepository / ProgressRepository 인터페이스
    storage/localStorageRepository.ts ← 기존 localStorage 키(noriUser, ck.bN.sub.done 등) 그대로 사용하는 구현체
    hooks/useAccount.ts, useStageCompletion.ts
    styles/account.css       ← A_account.css 포팅
```
- **중요**: `localStorageRepository`는 새 스키마를 만들지 않고 기존 레거시 키(`noriUser`, `ck.bN.sub.done`, `noriAttend`, `sessionStorage.noriAuth`)를 그대로 읽고 쓴다. iframe 안의 허브/메뉴 페이지들도 이 키를 직접 읽기 때문에, React만의 새 스키마를 쓰면 게임 내 진행도 UI가 깨진다.
- 이 인터페이스 뒤에서만 구현을 바꾸면 되므로, 추후 Firebase/Firestore 전환 시에도 호출부(컴포넌트/훅)는 그대로 둔 채 구현체만 교체 가능.

## 4. 로컬 스토리지 공유 ? 개발 환경 주의점
- 운영(GitHub Pages)에서는 React 빌드와 `public/game/**`가 같은 origin이라 iframe과 부모가 localStorage를 자연스럽게 공유함.
- 개발 중에도 `public/game/`을 Vite 자체 dev 서버가 서빙하므로 **게임 파일을 별도 포트/프로세스로 띄우지 않는 한** 문제 없음 ? 이 규칙을 README에 명시.

## 5. GitHub Pages 배포 전환
- `.github/workflows/deploy.yml` 추가: `npm ci` → `npm run build` → `dist/`를 Pages 아티팩트로 업로드/배포.
- CI 러너는 `E:` 드라이브(디자이너 SVN)에 접근할 수 없으므로, `public/game/`은 동기화 스크립트를 로컬에서 실행한 결과를 **커밋해서 저장소에 포함**시킨다(디자이너 쪽 변경이 있을 때마다 로컬에서 재실행 후 커밋/푸시).
- 저장소 Settings → Pages의 Source를 "Deploy from a branch(main root)"에서 **"GitHub Actions"**로 변경해야 함.
- 전환 후에는 `clius-dev.github.io/kindercoding/B_0_main/A-1_login.html` 같은 기존 직접 URL들이 더 이상 그대로 동작하지 않음(루트가 React 앱이 되고, 게임 파일은 `/game/...` 하위로 이동) ? 이미 "React 앱으로 교체" 결정에 포함된 당연한 결과지만, 실제로 Pages 설정을 바꾸는 시점에 한 번 더 확인받고 진행.

## 6. Git/GitHub ? 별도 확인 필요한 위험 단계
- `H:\test`에 `git init` 후 `origin`을 `https://github.com/clius-dev/kindercoding.git`로 설정, 로컬에서 자유롭게 커밋.
- 기존 `main`은 이번 작업과 공통 조상이 없는 별개 히스토리라, 그대로 push하면 거부되거나 **강제 push(히스토리 덮어쓰기)**가 필요함.
- **이 단계는 지금 계획을 승인한다고 해서 자동으로 진행하지 않음.** 실제로 push하기 직전에 다시 한번 구체적으로 여쭤서(강제 push vs 새 브랜치로 올린 뒤 전환 vs 기존 main을 다른 이름으로 보존 등) 명시적으로 확인받고 진행.

## 7. 단계별 작업 + 검증
1. **스캐폴드**: `npm create vite@latest . -- --template react-ts` → `npm run dev`로 기본 페이지 확인.
2. **동기화 스크립트(B-1 테마만)**: BFS 결과를 `sync-report.json`으로 확인, `public/game/B-1_어린이집과친구/...`를 브라우저로 직접 열어 이미지/폰트 404 없는지, `_old`/죽은 파일이 복사 안 됐는지 확인.
3. **전체 테마 확장**: 6개 테마 전부 동기화, 재실행 멱등성 확인(두 번 돌려도 결과 동일).
4. **postMessage 훅 주입**: 생성된 HTML에서 주입 스니펫 존재 확인(스테이지 파일에만, 1개씩), 임시 테스트 페이지로 iframe에 넣어 스테이지 완료 시 `message` 이벤트가 올바른 `theme`/`stage`로 오는지 확인.
5. **계정/로그인 포팅**: `storage` 모듈 + `LoginPage` 구현, 로그인 후 `localStorage.noriUser`가 레거시 포맷과 동일한지 확인, 새로고침 시 로그인 유지 확인.
6. **GameFrame 연동(로컬 end-to-end)**: 로그인 → iframe 진입 → 게임 내 허브에서 B-1 스테이지 진입 → 완료 → `localStorage['ck.b1.sub.done']`에 기록되는지, 게임 내부 허브 UI에도 완료 표시가 반영되는지(= localStorage 공유가 실제로 되는지) 확인. 여기까지는 전부 로컬에서 끝남.
7. **배포 전환(별도 확인 후 진행)**: 위 6번 단계로 전체 로컬 검증이 끝난 뒤에만 진행. `public/game` 포함 전체 커밋 → 워크플로 추가 → git/GitHub 단계(6번 섹션)에서 사용자 확인 → push → Pages Source 변경 → 실제 배포 사이트에서 로그인~스테이지 완료까지 재확인.

## 핵심 파일
- `scripts/sync-game.mjs` ? 링크 추적 복사 + postMessage 주입, 모든 것의 기반.
- `src/storage/types.ts`, `src/storage/localStorageRepository.ts` ? 레거시 키와 호환되어야 하는 저장소 추상화.
- `src/components/GameFrame.tsx` ? iframe + postMessage 리스너.
- `src/routes/LoginPage.tsx` ? `A-1_login.html`/`A_account.js` 포팅.
- `.github/workflows/deploy.yml` ? 새 배포 파이프라인.