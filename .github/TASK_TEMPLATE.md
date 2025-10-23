# Task Specification Template

**목적**: 모든 작업 명세에 Constitution 맥락을 포함하여 방향성 상실 방지

---

## 작업 정보

### 작업명
[작업의 간단한 제목]

### Phase / 일정
- **Phase**: [예: Phase E Week 1]
- **예상 시간**: [예: 2시간]
- **우선순위**: [High / Medium / Low]

---

## Constitution 맥락 (필수!)

### 연결된 조항
이 작업이 강화/개선하는 Constitution 조항을 명시하세요.

- [ ] **P1**: YAML 계약서 우선
- [ ] **P2**: 증거 기반 개발
- [ ] **P3**: 지식 자산화
- [ ] **P4**: SOLID 원칙
- [ ] **P5**: 보안 우선
- [ ] **P6**: 품질 게이트
- [ ] **P7**: Hallucination 방지
- [ ] **P8**: 테스트 우선
- [ ] **P9**: Conventional Commits
- [ ] **P10**: Windows 인코딩

**설명**: [어떻게 위 조항과 연결되는지 1-2문장으로 설명]

### 7계층 아키텍처 위치

이 작업이 영향을 주는 계층을 표시하세요.

- [ ] **Layer 1**: Constitution (헌법)
- [ ] **Layer 2**: Execution System (TaskExecutor, Validator)
- [ ] **Layer 3**: Analysis Engine (DeepAnalyzer, Aggregator)
- [ ] **Layer 4**: Optimization (Cache, Detector)
- [ ] **Layer 5**: Evidence Collection
- [ ] **Layer 6**: Knowledge Asset (ObsidianBridge)
- [ ] **Layer 7**: Visualization (Dashboard)

**주요 영향 계층**: [Layer X - 간단한 설명]

### 실행형 자산 시스템과의 연결

이 작업이 다음 핵심 개념과 어떻게 연결되는지 설명하세요:

**1. 문서가 곧 코드**
- [YAML 계약서와의 관계 또는 "해당 없음"]

**2. Constitution 중심**
- [어느 조항을 강화하는가?]

**3. 증거 기반 + 지식 자산화**
- [실행 결과 기록 방식 또는 Obsidian 동기화 관련]

---

## 작업 목표

### 무엇을 만드는가? (What)
[구체적 산출물, 예: "DeepAnalyzer에 P7 Hallucination 탐지 기능 추가"]

### 왜 만드는가? (Why)
[비즈니스/기술적 이유, Constitution 조항 강화 관점에서 설명]

### 어떻게 만드는가? (How)
[구현 방식, 기술 스택, 핵심 알고리즘]

---

## 우리가 만드는 것이 **아닌** 것 (NOT)

**중요**: 방향성 상실을 방지하기 위해 명시적으로 제외 범위를 정의합니다.

이 작업에서 다음은 **하지 않습니다**:

- [ ] 독립적 도구 개발 (모든 도구는 Constitution 조항 강제가 목적)
- [ ] UI/UX 최적화 (대시보드는 Layer 7 시각화일 뿐)
- [ ] 완성된 프로덕트 개발 (스타터킷 = 기준 체계 템플릿)
- [ ] [기타 제외 사항]

**예시**:
```
❌ "대시보드를 더 예쁘게 만들기" → Layer 7은 단순 시각화
✅ "대시보드에 P6 조항 준수 현황 표시" → Constitution 중심
```

---

## 성공 기준

### 기능적 성공
- [ ] [기능이 정상 작동]
- [ ] [테스트 통과]
- [ ] [문서화 완료]

### Constitution 준수
- [ ] 해당 조항 강화 확인
- [ ] 7계층 아키텍처 유지
- [ ] 실행형 자산 시스템 개념 부합

### 품질 기준
- [ ] `pytest` 통과
- [ ] `ruff check` 통과
- [ ] Coverage ≥ 90%
- [ ] Quality Score ≥ 7.0

---

## 기술 명세

### 수정/생성 파일
```
scripts/
  ├── [파일명.py] - [역할]
  └── ...

tests/
  ├── [테스트파일.py] - [테스트 범위]
  └── ...
```

### 의존성
```yaml
새 라이브러리: [없음 / 목록]
Python 버전: 3.12+
기존 컴포넌트: [활용하는 기존 도구]
```

### 핵심 로직
```python
# 핵심 알고리즘 또는 데이터 구조 설명
# (구체적 구현 아님, 개념만)
```

---

## 위험 요소 및 완화

### 잠재적 위험
1. **[위험 1]**
   - 영향도: [High / Medium / Low]
   - 완화 방안: [대응 전략]

2. **방향성 상실 위험**
   - 영향도: High
   - 완화 방안: NORTH_STAR.md 참조, Constitution 맥락 명시

### 롤백 전략
[실패 시 복구 방법]

---

## 체크리스트 (작업 시작 전)

작업을 시작하기 전에 다음을 확인하세요:

- [ ] **NORTH_STAR.md 읽기** (1분) - 방향성 재확인
- [ ] **constitution.yaml 참조** - 관련 조항 확인
- [ ] **이 템플릿 모든 섹션 작성** - 특히 Constitution 맥락, NOT 섹션
- [ ] **7계층 중 위치 명확** - Layer 혼동 방지
- [ ] **성공 기준 구체적** - 모호함 제거

---

## 참고 자료

### 필수 문서
- `NORTH_STAR.md` - 프로젝트 정체성
- `config/constitution.yaml` - 헌법 전문
- `README.md` - 프로젝트 개요

### 관련 파일
- [기존 구현 참고할 파일들]

### 외부 자료
- [공식 문서, 라이브러리 문서 등]

---

## 작업 완료 후 검증

작업을 완료한 후 다음을 확인하세요:

### Constitution 준수 검증
```bash
# P4, P5 조항 검증 (DeepAnalyzer)
pytest tests/test_deep_analyzer.py

# P6 조항 검증 (Quality Gate)
python scripts/team_stats_aggregator.py

# 전체 테스트
pytest --cov
```

### 방향성 재확인

**P11 체크리스트 (원칙 충돌 검증)**:
- [ ] 과거 지시와 충돌하지 않았는가?
- [ ] 충돌 시 양측 관점을 고려했는가?
- [ ] 사용자가 의식적으로 선택했는가?

**P12 체크리스트 (트레이드오프 분석)**:
- [ ] Option A vs B를 명시했는가?
- [ ] 각 옵션의 장단점에 객관적 근거가 있는가?
- [ ] ROI 계산을 했는가?
- [ ] 추천에 명확한 근거가 있는가?

**일반 체크리스트**:
- [ ] 이 작업이 Constitution 조항을 강화했는가?
- [ ] 실행형 자산 시스템 개념에 부합하는가?
- [ ] NOT 섹션에 명시한 것을 하지 않았는가?

### 지식 자산화
- [ ] Obsidian에 작업 결과 동기화 확인 (3초 이내)
- [ ] RUNS/evidence/ 에 증거 파일 생성 확인
- [ ] RUNS/stats/ 에 통계 업데이트 확인

---

**버전**: 1.0.0
**최종 수정**: 2025-10-23
**사용 시기**: 모든 Phase 시작 전 필수 작성
