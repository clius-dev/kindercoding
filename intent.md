# Intent: 기존 HTML 게임의 React(iframe) 포팅

Author: PM. Status: draft.

## Problem
디자이너가 `E:\01_Work\06_KinderCoding\03-Work\Coding`(SVN 관리)에 작업해 둔 기존 HTML 게임(시작 파일: `B_0_main/A-1_login.html`)을 React 앱 안에서 그대로 보여줘야 한다. 디자인·조작·사운드는 원본과 동일하게 유지해야 하며, React 쪽에서 게임 내부 이벤트(스테이지 완료/점수)를 감지해 계정별로 기록하고 화면에 표시해야 한다. 디자이너 작업물은 수시로 변경되므로, HTML 재복사 → React 반영 작업이 반복적으로 요청될 수 있다.

## Proposed outcome
- `H:\test`에 Vite + TypeScript 기반 신규 React 프로젝트 생성 (작업 파일 위치)
- `A-1_login.html`에서 링크로 이어지는 전체 게임 플로우(모든 화면)를, 내부 로직/마크업을 수정하지 않고 `<iframe>`으로 감싸 표시
- 링크·이미지 경로를 추적해 실제로 쓰이는 파일만 SVN 원본에서 `H:\test`로 복사 (불필요한 파일 제외)
- 디자이너 작업물이 업데이트될 때마다 동일한 방식(경로 추적 → 필요 파일만 재복사 → React 쪽 반영)으로 반복 재동기화
- iframe ↔ React 간 `postMessage`로 "게임 종료/점수" 이벤트 전달
- 계정 정보(계정, 닉네임, 아바타, 나이)는 브라우저 내장 저장소(IndexedDB 등)에 로컬 저장, 별도 서버 없음 (1차 범위)
- 스테이지 완료 시 점수를 로컬 DB에 기록하고, 기존 HTML 안에 있는 완료 화면을 그대로 표시
- 작업 결과를 기존 GitHub 저장소 [clius-dev/kindercoding](https://github.com/clius-dev/kindercoding) (Public)에 업로드

## Affected users and systems
- 사용자: 아이들(키즈 대상 게임), 한 기기를 여러 계정이 공유할 가능성
- 플랫폼: 데스크톱 브라우저, 모바일, 태블릿
- 소스 시스템: `E:\01_Work\06_KinderCoding\03-Work\Coding` (SVN, 디자이너 작업물, 수시 변경됨) — 읽기 전용 참조
- 작업 시스템: `H:\test` (신규 Vite+TS React 프로젝트)
- 배포/협업 시스템: GitHub [clius-dev/kindercoding](https://github.com/clius-dev/kindercoding) (Public)
- (추후) Firebase Auth(구글/애플 로그인), Firestore — 서버 저장소로 확장 가능성

## Constraints
- 디자인·조작·사운드는 원본과 100% 동일하게 유지 (게임 내부는 그대로 iframe 임베드, 로직/마크업 변경 금지)
- 로그인 로직은 기존 HTML/JS에 이미 존재 → 그대로 활용, 계정 데이터 저장소만 로컬 DB(브라우저)로 연동
- 스테이지 완료 화면은 기존 HTML 안에 이미 존재 → 그대로 사용
- 디자이너 작업물은 수시로 바뀌므로 1회성 포팅이 아니라 반복 가능한 재동기화 작업(파일 추적/복사 절차)이 필요
- 1차 범위는 서버/백엔드 없음(전부 클라이언트 로컬 저장)이지만, 추후 Google/Apple 로그인 + Firebase/Firestore로 서버 저장소 전환이 예정 → 계정/점수 데이터 저장 로직은 로컬↔서버 전환이 쉬운 구조(저장소 추상화)로 설계할 필요
- 모바일/태블릿 사운드 autoplay 등 브라우저 정책 제약 가능성 있음
- 최종 결과물은 Public GitHub 저장소에 업로드되므로, 민감 정보(키/시크릿 등)가 커밋에 포함되지 않도록 주의

## Open questions
- 계정 생성/로그인 시 비밀번호 필요 여부 및 검증 수준
- iframe 반응형 처리(모바일/태블릿 화면 크기 대응) 세부 방식
- Firebase/Firestore 전환 시점 및 1차 범위에서 어느 정도까지 미리 대비해둘지 (저장소 인터페이스 분리 시점)
- GitHub 저장소에 기존 코드/구조가 있는지, 그 위에 새 프로젝트를 올리는 건지 또는 저장소를 비우고 새로 시작하는지
- 작업 실행 방식: 파일 동기화/React 구현/GitHub 업로드 등을 여러 에이전트(세션)로 나눠 진행할지, 한 세션에서 순차적으로 진행할지
