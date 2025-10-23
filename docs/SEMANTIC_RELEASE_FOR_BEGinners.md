# Semantic Release & 환경 준비 빠르게 이해하기

## 1. 왜 Semantic Release를 쓰나요?
- 커밋 메시지(`feat:`, `fix:`, `docs:` 등)를 읽고 **버전을 자동**으로 올려줘요.
- CHANGELOG, Git 태그, GitHub Release까지 **원클릭 자동화**됩니다.
- 릴리스 담당자가 버전 번호를 기억하거나 문서를 수동으로 만들 필요가 없어집니다.

## 2. 필요한 기본 개념
- **Conventional Commits**: `feat(scope): 메시지`처럼 약속된 형식으로 커밋을 남기는 규칙이에요. 이 형식이 semantic-release가 동작하는 재료입니다.
- **의존성 설치**: `npm install --no-fund --no-audit` 명령으로 semantic-release가 사용하는 패키지를 내려 받아야 실행이 가능합니다. (Python에서 `pip install`과 같은 의미.)
- **Node 버전 고정**: `.nvmrc` 파일에 적힌 `20` 버전을 `nvm use 20`으로 맞추면, 팀/CI/내 PC가 동일한 Node 환경을 쓰게 됩니다.

## 3. 단계별 체크 리스트
1. **Node 20 활성화**
   ```bash
   nvm install 20   # 한 번만 설치
   nvm use 20       # 작업할 때마다 활성화
   ```
2. **환경 점검 스크립트 실행**
   ```bash
   python scripts/check_release_env.py
   ```
   - Node·npm 설치 여부, `.nvmrc` 버전 일치, `node_modules` 존재 여부를 한 번에 확인합니다.
3. **의존성 설치**
   ```bash
   npm install --no-fund --no-audit
   ```
   - `node_modules/`가 생기면 semantic-release가 필요한 플러그인을 사용할 수 있습니다.
4. **릴리스 드라이런**
   ```bash
   npm run release -- --dry-run
   ```
   - 실제 태그를 만들지 않고 “릴리스가 어떻게 돌아갈지” 미리 볼 수 있습니다.
5. **package-lock 생성 (네트워크 가능할 때)**
   ```bash
   npm install --package-lock-only --ignore-scripts --no-fund --no-audit
   ```
   - `package-lock.json`을 커밋하면 CI와 로컬에서 동일한 버전을 사용하게 됩니다.

## 4. 초보자가 기억하면 좋은 포인트
- **UTC 타임스탬프**: `datetime.now(timezone.utc)`를 쓰면 어디서 실행해도 시간이 일관돼서 로그 분석이 쉬워요.
- **검증 루틴**: `python -m pytest -q` 같은 표준 테스트를 변경 후마다 실행하는 습관이 품질을 지켜줍니다.
- **경고를 읽어보기**: 스크립트가 출력하는 경고를 천천히 읽고 해결하는 연습이 문제 해결 능력을 빠르게 키웁니다.

## 5. 다음에 할 일
- `npm run release -- --dry-run` 로그를 읽어보고 버전이 어떻게 계산되는지 눈에 익혀보세요.
- GitHub Actions에서 semantic-release 워크플로우가 어떻게 동작하는지 확인하고, 필요하면 `GITHUB_TOKEN` 권한을 점검해 주세요.
- 릴리스 자동화가 익숙해지면 Conventional Commits 규칙을 팀 전체에 적용해 재현 가능한 릴리스 문화를 만들어 보세요.
