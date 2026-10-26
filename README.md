# KinderCoding (React port)

디자이너가 SVN으로 관리하는 기존 HTML 키즈 코딩 게임을, React(Vite+TypeScript) 앱에서 로그인/계정은 React가 담당하고 게임 자체는 `<iframe>`으로 그대로 보여주는 방식으로 포팅한 프로젝트입니다.

배경/결정 사항은 [intent.md](./intent.md)와 [plan.md](./plan.md)에 정리되어 있습니다. 먼저 읽어보세요.

## 배포
- 운영: https://clius-dev.github.io/kindercoding/ — `main`에 push하면 `.github/workflows/deploy.yml`이 자동으로 빌드 후 배포합니다.
- 기존 원본 HTML 미러(이 작업 전 운영 중이던 버전)는 `legacy-static` 브랜치에 그대로 보존되어 있습니다.

## 로컬 개발 환경 준비
1. Node.js 20+ 설치
2. 이 저장소 clone
3. `npm install`
4. `npm run dev` → http://localhost:5173

## 게임 에셋 동기화 (디자이너 작업물이 바뀌었을 때)
게임 HTML/이미지/오디오는 `public/game/`에 들어있는데, 이건 사람이 직접 수정하는 폴더가 아니라 `scripts/sync-game.mjs`가 디자이너의 SVN 원본에서 **실제로 링크로 연결된 파일만** 추적해서 자동 복사한 결과물입니다 (원본 전체가 1.6GB가 넘고 상당수가 죽은 초안이라, 필요한 파일만 추립니다). 실행할 때마다 `public/game/`을 통째로 비우고 다시 채웁니다.

```bash
node scripts/sync-game.mjs --source "<내 PC의 SVN 작업 복사본 경로>"
```

- `--source`를 생략하면 스크립트에 하드코딩된 기본 경로(`E:\01_Work\06_KinderCoding\03-Work\Coding`, 이 프로젝트를 처음 만든 PC 기준)를 씁니다. **다른 PC에서는 본인의 SVN 체크아웃 경로를 `--source`로 꼭 지정하세요.**
- `--dry-run`을 붙이면 복사 없이 `scripts/sync-report.json`만 생성합니다 (어떤 파일이 발견/누락됐는지 확인용).
- `--theme B-1`처럼 테마를 지정하면 해당 테마 + 공통 파일만 복사해서 빠르게 확인할 수 있습니다 (단, 링크 탐색 자체는 항상 전체를 돕니다).
- 동기화 후에는 스테이지 HTML에 `postMessage` 완료 알림 훅이 자동으로 다시 주입됩니다. 디자이너 원본은 절대 수정하지 않습니다.
- 동기화 결과(`public/game/`)는 CI가 디자이너 SVN에 접근할 수 없어서 **저장소에 커밋**해야 배포에 반영됩니다. 동기화 → 확인 → 커밋 → push 순서입니다.

## 구조
```
src/
  App.tsx                 로그인 여부에 따라 LoginPage ↔ GameFrame 전환
  routes/LoginPage.tsx     원본 A-1_login.html/A_account.js를 React로 포팅 (같은 CSS·localStorage 키 사용)
  components/GameFrame.tsx 게임을 담는 <iframe> + postMessage로 스테이지 완료 감지
  storage/                 AccountRepository / ProgressRepository — 지금은 localStorage 구현체뿐,
                            나중에 Firebase/Firestore로 바꿀 때 이 인터페이스 뒤에서만 교체하면 됨
public/game/               동기화 스크립트가 생성 (직접 수정 금지)
scripts/sync-game.mjs      동기화 + postMessage 훅 주입 스크립트
```

## 알려진 제약/미완 항목
- `B-6_건강과자연` 테마는 디자이너 소스에 폴더는 있지만 아직 실제 메뉴/링크에 연결돼 있지 않아 자동으로 제외됩니다. 디자이너가 연결하면 다음 동기화 때 자동으로 포함됩니다.
- 전체메뉴(`A-4_allmenu.html`) 안의 장식용 테마 아이콘 중 일부는 경로가 동적으로 조합돼서 자동 추적이 못 찾는 경우가 있습니다 (`scripts/sync-report.json`의 `unresolved` 목록 참고). 핵심 페이지/스크립트는 전부 추적되고, 이 목록엔 장식용 이미지만 남아있는 걸 확인했습니다.
- 로그인은 원본과 동일하게 목업입니다(비밀번호 저장/검증 안 함). 구글/애플 로그인·Firebase 연동은 계획에 포함돼 있지만 아직 구현 전입니다.
