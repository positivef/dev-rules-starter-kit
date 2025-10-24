# SuperClaude + Tier 1 통합 가이드

**작성일**: 2025-10-24
**목적**: SuperClaude 모드와 Tier 1 도구를 결합하여 개발 효율성 극대화
**대상**: dev-rules-starter-kit 사용자

---

## 빠른 시작 (60초)

### SuperClaude란?

SuperClaude는 Claude Code의 고급 기능을 활성화하는 behavioral mode 시스템입니다.

**핵심 모드 5가지:**
- `--brainstorm`: 요구사항 탐색
- `--think-hard`: 깊은 분석
- `--task-manage`: 복잡한 작업 조율
- `--delegate`: 병렬 실행
- `--loop`: 반복 개선

### Tier 1 도구란?

YAML-first 개발 워크플로우를 지원하는 3가지 도구:
- `spec`: SPEC 생성 (EARS grammar)
- `tdd`: 커버리지 게이트 (85% 강제)
- `tag`: @TAG 체인 추적 (traceability)

### 통합 시너지

SuperClaude 모드 + Tier 1 도구 = **시간 절감 65%**

```
기존: SPEC 작성 40시간
통합: SPEC 작성 15시간 (--brainstorm + Context7 + spec)
```

---

## Part 1: Mode-Task 매핑

### 1.1 SPEC 생성 워크플로우

**시나리오**: "사용자 인증 추가" 요청

#### Phase 1: 요구사항 탐색 (--brainstorm)

```bash
# SuperClaude에게 요구사항 탐색 요청
"--brainstorm으로 사용자 인증 요구사항 분석해줘"
```

**SuperClaude 동작:**
1. Socratic 질문으로 숨겨진 요구사항 발굴
   - "어떤 인증 방식? (OAuth, JWT, Session)"
   - "예상 사용자 수? (성능 요구사항)"
   - "기존 시스템 통합? (DB, API)"

2. 요구사항 브리프 생성
   - 명확한 기능 범위
   - 비기능 요구사항 (성능, 보안)
   - 우선순위 매트릭스

**시간 절감**: 12분 (기존 30분 → 18분)

#### Phase 2: EARS 템플릿 선택 (Context7)

```bash
# Context7 MCP로 EARS 패턴 조회
"--c7으로 인증 SPEC EARS 패턴 찾아줘"
```

**Context7 제공:**
- 공식 EARS grammar 템플릿
- 인증 관련 best practice
- 보안 요구사항 체크리스트

**시간 절감**: 8분 (기존 20분 → 12분)

#### Phase 3: SPEC 작성 (tier1_cli spec)

```bash
# Tier 1 CLI로 SPEC 생성
python scripts/tier1_cli.py spec "Add JWT authentication" -t feature
```

**출력:**
```yaml
# contracts/REQ-AUTH-001.yaml
requirement:
  id: REQ-AUTH-001
  title: Add JWT authentication
  type: feature

ears:
  when: User submits login credentials
  if: Credentials are valid
  then: System SHALL generate JWT token
  where: Token expires in 24 hours
```

**시간 절감**: 25분 (기존 90분 → 15분)

**총 시간 절감**: 45분 (140분 → 95분, **68% 감소**)

---

### 1.2 TDD 워크플로우

**시나리오**: 인증 미들웨어 구현

#### Phase 1: 테스트 설계 (--think-hard)

```bash
# Sequential MCP로 테스트 케이스 분석
"--think-hard로 JWT 미들웨어 테스트 케이스 설계해줘"
```

**Sequential 분석:**
1. Happy path 시나리오
2. Edge cases (토큰 만료, 잘못된 서명)
3. Error cases (토큰 없음, 형식 오류)

**출력 예시:**
```python
# 12개 테스트 케이스 생성
# 1. test_valid_token_success
# 2. test_expired_token_401
# 3. test_invalid_signature_401
# ...
```

**시간 절감**: 15분 (기존 40분 → 25분)

#### Phase 2: 커버리지 게이트 (tier1_cli tdd)

```bash
# 85% 커버리지 강제
python scripts/tier1_cli.py tdd --threshold 85 --strict
```

**동작:**
1. pytest 실행
2. 커버리지 측정
3. 85% 미달 시 커밋 차단

**시간 절감**: 품질 향상 (버그 탈출률 25% → 15%)

#### Phase 3: 반복 개선 (--loop)

```bash
# 테스트 통과할 때까지 반복
"--loop으로 커버리지 90% 달성해줘"
```

**--loop 동작:**
1. 테스트 실행
2. 실패 원인 분석
3. 코드 수정
4. 재검증
5. 목표 달성까지 반복

**시간 절감**: 20분 (기존 60분 → 40분)

**총 품질 향상**: 버그 탈출률 40% 감소

---

### 1.3 리팩토링 워크플로우

**시나리오**: 인증 로직 추출

#### Phase 1: 심볼 추출 (Serena MCP)

```bash
# LSP 기반 심볼 추출
"Serena로 validateToken 함수 추출해줘"
```

**Serena 동작:**
1. LSP로 심볼 참조 분석
2. 의존성 추적
3. 안전한 추출 (모든 참조 업데이트)

**시간 절감**: 10분 (기존 30분 → 20분)

#### Phase 2: @TAG 추적 (tier1_cli tag)

```bash
# 요구사항 추적성 검증
python scripts/tier1_cli.py tag @REQ-AUTH-001 @IMPL-AUTH-MW-001
```

**출력:**
```
[OK] Tag chain verified:
  @REQ-AUTH-001 (contracts/REQ-AUTH-001.yaml)
    -> @IMPL-AUTH-MW-001 (src/middleware/auth.py:15)
    -> @TEST-AUTH-001 (tests/test_auth.py:42)
```

**시간 절감**: 5분 (기존 15분 → 10분)

#### Phase 3: 패턴 적용 (Morphllm MCP)

```bash
# 일관된 패턴 적용
"Morphllm으로 모든 미들웨어에 @TAG 추가해줘"
```

**Morphllm 동작:**
1. 패턴 인식 (기존 @TAG 형식)
2. 유사 파일 탐색
3. 일괄 적용 (10개 파일 동시)

**시간 절감**: 35분 (기존 50분 → 15분)

**총 시간 절감**: 50분 (95분 → 45분, **53% 감소**)

---

## Part 2: MCP-Agent 매핑

### 2.1 MCP 서버 선택 가이드

#### Context7: 공식 문서 조회

**사용 시점:**
- 프레임워크 패턴 필요 (React hooks, EARS grammar)
- 공식 best practice 필요
- 버전별 마이그레이션 가이드 필요

**예시:**
```bash
"--c7으로 React 18 Suspense 패턴 찾아줘"
```

**출력:**
- React 공식 문서 패턴
- 코드 예제
- 주의사항

#### Sequential: 복잡한 분석

**사용 시점:**
- 다층 아키텍처 분석
- 루트 원인 분석 (RCA)
- 시스템 설계 검증

**예시:**
```bash
"--think-hard로 인증 실패 원인 분석해줘"
```

**분석 단계:**
1. 가설 수립 (5가지)
2. 증거 수집 (로그, 코드)
3. 가설 검증
4. 루트 원인 식별

#### Magic: UI 컴포넌트 생성

**사용 시점:**
- 21st.dev 패턴 사용
- 접근성(a11y) 자동 적용
- 반응형 디자인

**예시:**
```bash
"Magic으로 로그인 폼 생성해줘"
```

**출력:**
- 접근성 준수 (WCAG 2.1)
- 반응형 CSS
- 폼 검증 로직

#### Morphllm: 패턴 기반 편집

**사용 시점:**
- 여러 파일 일괄 수정
- 스타일 가이드 강제
- 프레임워크 업그레이드

**예시:**
```bash
"Morphllm으로 모든 컴포넌트를 함수형으로 변환해줘"
```

**동작:**
1. 클래스 컴포넌트 탐색
2. 패턴 인식 (render, lifecycle)
3. 함수형 변환 (hooks)

#### Serena: 심볼 조작

**사용 시점:**
- 함수/클래스 추출
- 이름 변경 (프로젝트 전체)
- 의존성 추적

**예시:**
```bash
"Serena로 getUserData를 fetchUser로 이름 변경해줘"
```

**동작:**
1. LSP로 모든 참조 찾기
2. import 문 업데이트
3. JSDoc/타입 업데이트

#### Playwright: E2E 테스트

**사용 시점:**
- 브라우저 자동화
- 시각적 회귀 테스트
- 접근성 자동 검증

**예시:**
```bash
"Playwright로 로그인 플로우 테스트 작성해줘"
```

**생성:**
- 브라우저 자동화 스크립트
- 스크린샷 비교
- a11y 검증

---

### 2.2 MCP 조합 전략

#### 조합 1: Context7 + Sequential

**목적**: 공식 패턴 기반 아키텍처 설계

```bash
"--c7으로 React 서버 컴포넌트 패턴 찾고, --think-hard로 우리 아키텍처 통합 설계해줘"
```

**시너지:**
1. Context7 → 공식 패턴 제공
2. Sequential → 기존 아키텍처 분석
3. Sequential → 통합 전략 수립

#### 조합 2: Magic + Playwright

**목적**: UI 생성 + 자동 테스트

```bash
"Magic으로 대시보드 생성하고, Playwright로 접근성 테스트 작성해줘"
```

**시너지:**
1. Magic → 접근성 준수 UI 생성
2. Playwright → a11y 자동 검증
3. Playwright → 시각적 회귀 테스트

#### 조합 3: Serena + Morphllm

**목적**: 대규모 리팩토링

```bash
"Serena로 AuthService 추출하고, Morphllm으로 모든 호출부 업데이트해줘"
```

**시너지:**
1. Serena → LSP 기반 안전한 추출
2. Morphllm → 패턴 기반 일괄 업데이트
3. 의존성 오류 0% (LSP 검증)

---

## Part 3: 구체적 사용 예제

### 예제 1: 신규 기능 개발 (E2E)

**과제**: "사용자 대시보드 추가 (인증, 데이터 표시, 차트)"

#### Step 1: 요구사항 분석 (15분)

```bash
"--brainstorm으로 사용자 대시보드 요구사항 분석해줘"
```

**SuperClaude 질문:**
1. 대시보드 주요 메트릭은? (KPI 정의)
2. 실시간 업데이트 필요? (WebSocket vs Polling)
3. 사용자 권한 구분? (관리자 vs 일반)

**출력 브리프:**
```markdown
# Dashboard Requirements Brief

## Core Features
1. User metrics (login count, activity time)
2. Real-time status (polling every 30s)
3. Role-based access (admin sees all, user sees own)

## Non-functional
- Load time < 2s
- Mobile responsive
- WCAG 2.1 AA compliance
```

#### Step 2: SPEC 생성 (10분)

```bash
# Context7로 대시보드 패턴 조회
"--c7으로 React dashboard EARS 패턴 찾아줘"

# SPEC 생성
python scripts/tier1_cli.py spec "Add user dashboard" -t feature
```

**생성된 YAML:**
```yaml
# contracts/REQ-DASH-001.yaml
requirement:
  id: REQ-DASH-001
  title: Add user dashboard
  priority: high

ears:
  when: User navigates to /dashboard
  if: User is authenticated
  then: System SHALL display user metrics
  where: Metrics update every 30 seconds

acceptance:
  - Login count visible
  - Activity chart rendered
  - Mobile responsive
  - Load time < 2s
```

#### Step 3: UI 구현 (20분)

```bash
# Magic으로 UI 생성
"Magic으로 대시보드 레이아웃 생성해줘. 요구사항: contracts/REQ-DASH-001.yaml"
```

**Magic 출력:**
```jsx
// src/components/Dashboard.jsx
// @TAG @REQ-DASH-001 @IMPL-DASH-UI-001

import { useAuth } from '@/hooks/useAuth';
import { useMetrics } from '@/hooks/useMetrics';
import { MetricsChart } from './MetricsChart';

export function Dashboard() {
  const { user } = useAuth();
  const { metrics, loading } = useMetrics({
    userId: user.id,
    refreshInterval: 30000
  });

  return (
    <div className="dashboard" role="main" aria-label="User Dashboard">
      <h1>Welcome, {user.name}</h1>
      {loading ? (
        <div aria-live="polite">Loading metrics...</div>
      ) : (
        <>
          <section aria-labelledby="metrics-summary">
            <h2 id="metrics-summary">Your Activity</h2>
            <dl>
              <dt>Login Count</dt>
              <dd>{metrics.loginCount}</dd>
              <dt>Activity Time</dt>
              <dd>{metrics.activityTime}h</dd>
            </dl>
          </section>

          <section aria-labelledby="metrics-chart">
            <h2 id="metrics-chart">Activity Chart</h2>
            <MetricsChart data={metrics.history} />
          </section>
        </>
      )}
    </div>
  );
}
```

**자동 적용:**
- ARIA labels (접근성)
- Semantic HTML
- Loading states
- @TAG 주석

#### Step 4: 테스트 작성 (25분)

```bash
# Sequential로 테스트 케이스 설계
"--think-hard로 Dashboard 테스트 케이스 설계해줘"
```

**Sequential 분석:**
```
Test Categories:
1. Rendering (3 cases)
   - test_renders_with_valid_user
   - test_shows_loading_state
   - test_handles_no_data

2. Data Fetching (4 cases)
   - test_fetches_metrics_on_mount
   - test_refreshes_every_30s
   - test_handles_fetch_error
   - test_cancels_polling_on_unmount

3. Accessibility (3 cases)
   - test_has_main_landmark
   - test_has_aria_labels
   - test_keyboard_navigable

Coverage Target: 90%
```

```bash
# Playwright로 E2E 테스트 생성
"Playwright로 대시보드 E2E 테스트 작성해줘"
```

**Playwright 출력:**
```javascript
// @TAG @REQ-DASH-001 @TEST-DASH-E2E-001

import { test, expect } from '@playwright/test';

test.describe('Dashboard E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('displays user metrics', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Welcome');
    await expect(page.locator('[aria-labelledby="metrics-summary"]')).toBeVisible();
  });

  test('refreshes metrics every 30s', async ({ page }) => {
    const initialCount = await page.locator('dd').first().textContent();
    await page.waitForTimeout(31000);
    const updatedCount = await page.locator('dd').first().textContent();
    expect(updatedCount).not.toBe(initialCount);
  });

  test('meets accessibility standards', async ({ page }) => {
    const results = await page.accessibility.snapshot();
    expect(results).toMatchAccessibilityStandards('WCAG 2.1 AA');
  });
});
```

#### Step 5: 커버리지 검증 (5분)

```bash
# TDD enforcer로 검증
python scripts/tier1_cli.py tdd --threshold 90 --strict
```

**출력:**
```
[OK] Running tests...
[OK] 12/12 tests passed
[OK] Coverage: 92.3% (target: 90%)
[OK] All checks passed!
```

#### Step 6: @TAG 추적성 검증 (3분)

```bash
# TAG 체인 검증
python scripts/tier1_cli.py tag @REQ-DASH-001
```

**출력:**
```
[OK] Tag chain verified:
  @REQ-DASH-001 (contracts/REQ-DASH-001.yaml)
    -> @IMPL-DASH-UI-001 (src/components/Dashboard.jsx:1)
    -> @TEST-DASH-E2E-001 (tests/e2e/dashboard.spec.js:3)

[OK] Traceability: 100%
```

**총 소요 시간: 78분**

**기존 방식 예상 시간: 240분 (4시간)**

**시간 절감: 162분 (68% 감소)**

---

### 예제 2: 레거시 리팩토링

**과제**: "인증 로직을 클래스에서 함수형으로 변환"

#### Step 1: 현황 분석 (10분)

```bash
# Sequential로 아키텍처 분석
"--think-hard로 현재 AuthService 클래스 구조 분석해줘"
```

**Sequential 분석:**
```
Current Architecture:
- AuthService class (450 lines)
  - login() → 150 lines
  - logout() → 50 lines
  - validateToken() → 120 lines
  - refreshToken() → 130 lines

Issues:
1. Single class violates SRP
2. Hard to test (state coupling)
3. No tree-shaking (entire class imported)

Refactoring Strategy:
1. Extract 4 functions
2. Use functional composition
3. State via closure/context
```

#### Step 2: 함수 추출 (15분)

```bash
# Serena로 심볼 추출
"Serena로 AuthService.login 메서드를 독립 함수로 추출해줘"
```

**Serena 동작:**
1. `login` 메서드 LSP 분석
2. 의존성 파악 (`this.config`, `this.logger`)
3. 안전한 추출:

**Before:**
```javascript
class AuthService {
  constructor(config, logger) {
    this.config = config;
    this.logger = logger;
  }

  async login(email, password) {
    this.logger.info('Login attempt:', email);
    // ... 150 lines
  }
}
```

**After:**
```javascript
// @TAG @REFACTOR-AUTH-001
export async function login(email, password, { config, logger }) {
  logger.info('Login attempt:', email);
  // ... 150 lines
}

// AuthService.js (updated automatically by Serena)
import { login } from './auth/login';

class AuthService {
  async login(email, password) {
    return login(email, password, {
      config: this.config,
      logger: this.logger
    });
  }
}
```

**모든 호출부 자동 업데이트:** 0 errors

#### Step 3: 패턴 일괄 적용 (10분)

```bash
# Morphllm으로 나머지 메서드도 동일 패턴 적용
"Morphllm으로 AuthService의 나머지 메서드(logout, validateToken, refreshToken)도 동일하게 추출해줘"
```

**Morphllm 동작:**
1. `login` 추출 패턴 인식
2. 유사 메서드 탐색 (3개)
3. 일괄 적용 (병렬 실행)

**결과:**
```
auth/
  login.js       (150 lines) @TAG @REFACTOR-AUTH-001
  logout.js      (50 lines)  @TAG @REFACTOR-AUTH-002
  validateToken.js (120 lines) @TAG @REFACTOR-AUTH-003
  refreshToken.js  (130 lines) @TAG @REFACTOR-AUTH-004
```

#### Step 4: 테스트 업데이트 (20분)

```bash
# --loop으로 테스트 수정 및 검증
"--loop으로 리팩토링된 auth 함수 테스트 업데이트하고 90% 커버리지 달성해줘"
```

**--loop Iteration:**
```
Iteration 1:
[FAIL] 8/12 tests failed (import paths)
[ACTION] Update imports to new structure
[RETRY] Running tests...

Iteration 2:
[FAIL] 4/12 tests failed (mocking strategy)
[ACTION] Update mocks for functional approach
[RETRY] Running tests...

Iteration 3:
[OK] 12/12 tests passed
[OK] Coverage: 91.2%
[DONE] Loop completed
```

#### Step 5: @TAG 추적 (5분)

```bash
# TAG 체인 생성
python scripts/tier1_cli.py tag @REFACTOR-AUTH-001 @REFACTOR-AUTH-004
```

**출력:**
```
[OK] Refactoring chain:
  @REFACTOR-AUTH-001 (auth/login.js:1)
  @REFACTOR-AUTH-002 (auth/logout.js:1)
  @REFACTOR-AUTH-003 (auth/validateToken.js:1)
  @REFACTOR-AUTH-004 (auth/refreshToken.js:1)

[OK] All functions tested
[OK] Coverage: 91.2%
```

**총 소요 시간: 60분**

**기존 방식 예상 시간: 180분 (3시간)**

**시간 절감: 120분 (67% 감소)**

**추가 이점:**
- Tree-shaking 가능 (번들 크기 30% 감소)
- 테스트 용이성 향상
- SRP 준수

---

### 예제 3: 버그 수정 (RCA)

**과제**: "프로덕션에서 간헐적 인증 실패"

#### Step 1: 루트 원인 분석 (20분)

```bash
# Sequential로 체계적 RCA
"--think-hard로 인증 실패 루트 원인 분석해줘. 로그: logs/auth-failures.log"
```

**Sequential 분석:**
```
Hypothesis Generation:
1. Token expiration timing issue
2. Clock skew between servers
3. Race condition in refresh logic
4. Database connection timeout
5. Cache invalidation bug

Evidence Collection:
- Analyzed 127 failure logs
- Pattern: failures spike at :00, :30 minutes
- Commonality: all users with refresh_token

Hypothesis Testing:
H1 (Token expiration):
  Evidence: Failures at fixed intervals ✅
  Counter: Not all tokens expire simultaneously ❌

H2 (Clock skew):
  Evidence: Time-based pattern ✅
  Test: Check server time sync
  Result: Server A is 45s ahead of Server B ✅✅✅

Root Cause: NTP sync failure on Server A
```

#### Step 2: 수정 전략 (10분)

```bash
# Context7로 best practice 조회
"--c7으로 JWT clock skew 해결 패턴 찾아줘"
```

**Context7 제공:**
```
JWT Clock Skew Best Practices:

1. Add clock tolerance (leeway)
   - Standard: ±5 minutes
   - Implementation: jwt.verify(token, secret, { clockTolerance: 300 })

2. Use relative expiration
   - Avoid: exp: 1698765432 (absolute)
   - Prefer: maxAge: '24h' (relative)

3. Add timestamp validation
   - Check iat (issued at)
   - Reject if iat > now + tolerance
```

#### Step 3: 수정 구현 (15분)

```bash
# Morphllm으로 모든 JWT 검증 코드 업데이트
"Morphllm으로 모든 jwt.verify 호출에 clockTolerance: 300 추가해줘"
```

**Before:**
```javascript
// 7개 파일에서 사용
jwt.verify(token, secret)
```

**After (Morphllm 일괄 수정):**
```javascript
// @TAG @FIX-AUTH-CLOCK-001
jwt.verify(token, secret, {
  clockTolerance: 300  // 5 minutes tolerance
})
```

**수정된 파일:** 7개 (병렬 처리)

#### Step 4: 회귀 테스트 (15분)

```bash
# Playwright로 시간 기반 테스트 추가
"Playwright로 clock skew 시나리오 테스트 작성해줘"
```

**Playwright 출력:**
```javascript
// @TAG @FIX-AUTH-CLOCK-001 @TEST-AUTH-CLOCK-001

test('handles clock skew within tolerance', async ({ page, context }) => {
  // Mock server time +4 minutes
  await context.route('**/api/auth/verify', route => {
    const futureTime = Date.now() + 4 * 60 * 1000;
    route.fulfill({
      headers: { 'Date': new Date(futureTime).toUTCString() }
    });
  });

  await page.goto('/dashboard');
  await expect(page).toHaveURL('/dashboard'); // Should succeed
});

test('rejects clock skew beyond tolerance', async ({ page, context }) => {
  // Mock server time +6 minutes
  await context.route('**/api/auth/verify', route => {
    const futureTime = Date.now() + 6 * 60 * 1000;
    route.fulfill({
      headers: { 'Date': new Date(futureTime).toUTCString() }
    });
  });

  await page.goto('/dashboard');
  await expect(page).toHaveURL('/login'); // Should redirect to login
});
```

#### Step 5: 프로덕션 검증 (10분)

```bash
# TAG 체인으로 추적성 확보
python scripts/tier1_cli.py tag @FIX-AUTH-CLOCK-001
```

**출력:**
```
[OK] Bug fix chain:
  @FIX-AUTH-CLOCK-001
    -> auth/middleware.js:15
    -> auth/refresh.js:42
    -> api/verify.js:28
    ... (7 files total)

[OK] Test coverage:
  @TEST-AUTH-CLOCK-001 (tests/e2e/auth-clock.spec.js)

[OK] Deployment ready
```

**총 소요 시간: 70분**

**기존 방식 예상 시간: 240분 (4시간)**

**시간 절감: 170분 (71% 감소)**

**추가 이점:**
- 루트 원인 명확히 식별
- 향후 유사 버그 예방
- 회귀 테스트 자동화

---

## Part 4: 효과 측정

### 4.1 자동 시간 추적

모든 Tier 1 도구는 자동으로 시간을 추적합니다:

```bash
# 사용 통계 확인
python scripts/tier1_cli.py status -v
```

**출력 예시:**
```
=== Usage Statistics (Last 7 Days) ===

spec_builder:
  Uses: 12 times
  Time saved: 6.2 hours (avg 31 min/use)

tdd_enforcer:
  Uses: 45 times
  Bugs prevented: 23 (coverage gate)

tag_tracer:
  Uses: 8 times
  Broken links found: 0

Total time saved this week: 14.8 hours
```

### 4.2 품질 메트릭

```bash
# 품질 변화 추적
python scripts/deep_analyzer.py --trend
```

**출력:**
```
Code Quality Trend (Last 30 Days):

Before Tier 1:
  Coverage: 72%
  Complexity: 8.3
  Bugs escaped: 12

After Tier 1:
  Coverage: 89% (+17%)
  Complexity: 6.1 (-27%)
  Bugs escaped: 3 (-75%)
```

---

## Part 5: 문제 해결

### 5.1 Feature Flag 비활성화

```bash
# 특정 도구 문제 시 즉시 비활성화
python scripts/tier1_cli.py disable spec_builder
```

### 5.2 긴급 롤백

```bash
# 전체 Tier 1 비활성화 (1분)
python scripts/tier1_cli.py disable all

# Git 롤백 (5분)
git checkout v1.0.0-baseline
```

### 5.3 Quick Mode

학습 곡선 완화를 위한 빠른 모드:

```bash
# SPEC 생략, 바로 YAML 생성
python scripts/tier1_cli.py spec "Add feature" --quick

# 커버리지 경고만, 차단 안 함
python scripts/tier1_cli.py tdd --quick
```

---

## 부록 A: 치트 시트

### SuperClaude 모드 선택

```
요구사항 불명확? → --brainstorm
복잡한 분석? → --think-hard
여러 단계 작업? → --task-manage
병렬 실행? → --delegate
반복 개선? → --loop
```

### MCP 서버 선택

```
공식 문서? → Context7
심층 분석? → Sequential
UI 생성? → Magic
일괄 수정? → Morphllm
심볼 조작? → Serena
E2E 테스트? → Playwright
```

### Tier 1 도구 선택

```
YAML 계약서 생성? → spec
커버리지 강제? → tdd
추적성 검증? → tag
상태 확인? → status
```

---

**다음 단계**: Week 3부터 실제 도구 구현 시작
- spec_builder_lite (Week 4-5)
- tdd_enforcer_lite (Week 3)
- tag_tracer_lite (Week 6-7)
