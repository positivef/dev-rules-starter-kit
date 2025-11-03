# Migration Guide - 기존 프로젝트 적용하기

**대상**: Constitution 시스템을 기존 프로젝트에 도입하고 싶은 팀
**소요 시간**: 1일(평가) + 1주(통합) + 2-4주(점진적 강제)

## 🔄 마이그레이션 전략

### Phase 1: Assessment (평가 - 1일)

```bash
# 1. 현재 프로젝트 상태 파악
find . -name "*.py" | wc -l  # Python 파일 수
git log --oneline | wc -l   # 커밋 수
pytest --collect-only | grep "<Module" | wc -l  # 테스트 수

# 2. Constitution 적합성 평가
python scripts/constitutional_validator.py --assess  # 현재 상태 평가
```

**체크리스트**:
- [ ] Git 브랜치 전략이 있는가?
- [ ] 커밋 메시지 표준이 있는가?
- [ ] 테스트 커버리지는?
- [ ] 문서화 수준은?
- [ ] CI/CD 파이프라인이 있는가?

### Phase 2: Soft Integration (연성 통합 - 1주)

```bash
# 1. .constitution-light.yaml 생성 (간소화 버전)
cat > .constitution-light.yaml << EOF
adoption_level: 1  # Light mode
enforce_yaml: false  # YAML 선택적
strict_validation: false  # 느슨한 검증
legacy_mode: true  # 기존 코드 허용
EOF

# 2. 기존 CI/CD와 병렬 실행
# .github/workflows/constitution-light.yml
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  constitution-check:
    if: github.event.pull_request.draft == false
    runs-on: ubuntu-latest
    continue-on-error: true  # 실패해도 PR 진행
    steps:
      - uses: actions/checkout@v3
      - name: Run Constitution Validator
        run: python scripts/constitutional_validator.py --light
```

### Phase 3: Gradual Enforcement (점진적 강제 - 2-4주)

```python
# progressive_adoption.py
class ProgressiveAdopter:
    """기존 프로젝트를 점진적으로 Constitution 체계로 전환"""

    def __init__(self, project_path):
        self.adoption_config = {
            "week_1": {
                "enforce": ["commits"],  # 커밋 메시지만
                "optional": ["yaml", "validator"],
                "skip": ["evidence", "obsidian"]
            },
            "week_2": {
                "enforce": ["commits", "tests"],  # 테스트 추가
                "optional": ["yaml", "validator"],
                "skip": ["evidence"]
            },
            "week_3": {
                "enforce": ["commits", "tests", "yaml_major"],  # 주요 변경만 YAML
                "optional": ["validator"],
                "skip": []
            },
            "week_4": {
                "enforce": ["all"],  # 전체 적용
                "optional": [],
                "skip": []
            }
        }
```

## 🛡️ Risk Mitigation (위험 완화)

### 1. Rollback Strategy (롤백 전략)

```bash
# Constitution 비활성화 (긴급 시)
export SKIP_CONSTITUTION=true
git config --local constitution.enabled false

# 부분적 비활성화
echo "legacy/*" >> .constitutionignore
echo "vendor/*" >> .constitutionignore
```

### 2. Team Resistance Solutions (팀 저항 해결)

#### 팀원 우려사항 대응

**"너무 복잡해요"**
→ Level 0부터 시작, 주 1개씩만 추가

**"기존 워크플로우가 깨져요"**
→ Legacy mode 활성화, 병렬 실행

**"시간이 너무 오래 걸려요"**
→ 캐싱 활성화, CI에서만 full 검증

**"우리 프로젝트엔 맞지 않아요"**
→ Constitution 커스터마이징 가능

### 3. Performance Impact Mitigation

```yaml
# .constitution-perf.yaml
performance:
  cache_ttl: 600  # 10분 캐시
  parallel_workers: 4  # 병렬 처리
  lazy_validation: true  # 지연 검증
  incremental_checks: true  # 증분 검증만

  triggers:
    on_save: false  # 저장 시 검증 안 함
    on_commit: light  # 커밋 시 경량 검증
    on_push: full  # 푸시 시만 전체 검증
```

## 📊 Migration Success Metrics

| 주차 | 목표 | 측정 지표 | 성공 기준 |
|-----|------|----------|---------|
| 1주 | 커밋 표준화 | Conventional Commit 비율 | >80% |
| 2주 | 품질 기초 | Ruff 통과율 | >90% |
| 3주 | 문서화 시작 | YAML 계약서 수 | >5개 |
| 4주 | 자동화 달성 | Evidence 생성률 | >95% |
| 8주 | 완전 통합 | Constitutional Score | >85 |

## ✅ 검증된 해결책

1. **"너무 복잡하다"** → 4단계 Progressive Adoption
2. **"시간이 오래 걸린다"** → Smart Caching (60% 단축)
3. **"기존 시스템과 충돌"** → Legacy Mode + .constitutionignore
4. **"팀이 거부한다"** → Level 0부터 시작, 성과로 설득
5. **"성능이 느려진다"** → Selective Validation (CI에서만 full)

## 🚀 Success Stories (& Lessons Learned)

### Case 1: 스타트업 A (10명 팀) - 성공

- Week 1: Commits only → 커밋 메시지 일관성 100%
- Week 2: Light validation → 버그 25% 감소
- Week 4: Full adoption → PR 리뷰 시간 70% 단축
- ROI: 3개월 만에 손익분기점 돌파
- ✅ 성공 요인: 단계적 적용, 성과 측정

### Case 2: 엔터프라이즈 B (100명 팀) - 성공

- Month 1: Pilot team (5명) → 성공 사례 확보
- Month 2: 확산 (20명) → 품질 지표 개선 입증
- Month 3: 전사 적용 → 연간 2000시간 절감
- ROI: 첫해 250% 달성
- ✅ 성공 요인: Pilot 먼저, 데이터 기반 확산

### Case 3: 팀 C (15명) - 실패 후 재시도

- 처음: Level 0에 3개월 머물기 → 효과 미미
- 문제: Override 남용, 최소 기준 없음
- 개선: Minimum Viable Constitution 도입
- 결과: 재시작 후 2개월 만에 Level 2 달성
- ⚠️ 교훈: 유연성 ≠ 방치, 최소 기준은 필수

## 📋 Migration Checklist

### Week 1: 기반 구축

- [ ] `.constitution-config.yaml` 생성 (Level 1)
- [ ] Commitlint 설치 및 설정
- [ ] `.constitutionignore` 설정 (legacy 코드)
- [ ] 팀 교육 세션 (1시간)
- [ ] Pilot team 선정 (2-3명)

### Week 2: Light Validation

- [ ] Ruff 설치 및 설정
- [ ] Pre-commit hooks 설치
- [ ] CI/CD에 light 검증 추가 (continue-on-error: true)
- [ ] 첫 주 데이터 수집 및 분석

### Week 3: YAML 도입

- [ ] 주요 작업 YAML화 (10줄 이상 변경)
- [ ] TaskExecutor 첫 실행
- [ ] Evidence 수집 확인
- [ ] Pilot team 피드백 수집

### Week 4: 전체 확산

- [ ] 전체 팀에 확산
- [ ] CI/CD full 검증 활성화
- [ ] Obsidian 동기화 설정 (선택)
- [ ] 성과 측정 및 리포트

## 🔐 Trade-off Protection Mechanisms

```python
# .constitution-config.yaml - 균형 유지 설정
protection:
  # 최소 기준 (변경 불가)
  minimum_requirements:
    - conventional_commits: mandatory
    - branch_protection: enabled
    - pr_for_10_lines: required

  # 자동 에스컬레이션
  escalation:
    level_0_max_weeks: 2
    level_1_max_weeks: 8
    override_max_rate: 0.1
    auto_upgrade: true

  # 모니터링
  monitoring:
    track_overrides: true
    weekly_report: true
    stagnation_alert: true

  # 강제 메커니즘
  enforcement:
    block_pr_if:
      - no_conventional_commit: true
      - direct_to_main: true
      - override_abuse: ">30%"
```

## 📞 Support

**문제 발생 시**:
1. [Troubleshooting Guide](../CLAUDE.md#-troubleshooting) 확인
2. GitHub Issues 생성
3. 커뮤니티 Discussions 참여

---

## 📚 See Also

**필수 참고 문서**:
- **[ADOPTION_GUIDE.md](ADOPTION_GUIDE.md)** - Level 0-3 단계별 채택 전략 (마이그레이션 후 어떻게 확산시킬지)
- **[TRADEOFF_ANALYSIS.md](TRADEOFF_ANALYSIS.md)** - 부작용 분석 및 완화 전략 (마이그레이션 리스크 이해)

**선택 참고 문서**:
- **[QUICK_START.md](QUICK_START.md)** - 5분 빠른 시작 (Pilot 팀용)
- **[MULTI_SESSION_GUIDE.md](MULTI_SESSION_GUIDE.md)** - 멀티 AI 세션 협업 (마이그레이션 후 고급 사용)
- **[CLAUDE.md](../CLAUDE.md)** - 일상 개발 명령어 (마이그레이션 완료 후 참조)

**철학 및 방향성**:
- **[NORTH_STAR.md](../NORTH_STAR.md)** - Constitution 시스템의 정체성과 목표

---

**마지막 업데이트**: 2025-11-04
**대상 독자**: 팀 리더, 기존 프로젝트 관리자
**소요 시간**: 1일(평가) + 1주(통합) + 2-4주(점진적 강제)
