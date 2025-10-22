# Team Statistics Aggregator 사용자 가이드

**Phase C Week 2 Day 10-11 구현 완료**

## 개요

TeamStatsAggregator는 팀 전체의 코드 품질 통계를 수집하고 시각화하는 도구입니다.

## 주요 기능

### 1. 통계 수집
- VerificationCache에서 검증 결과 수집
- 파일별 품질 점수, 위반 사항, 통과율 계산
- Deep 모드 분석 결과 통합 (SOLID, 보안, 환각 위험)

### 2. 대시보드 생성
- 마크다운 형식의 팀 대시보드
- 품질 점수 분포 시각화 (ASCII 차트)
- 문제 파일 우선순위 목록
- 맞춤형 개선 권장사항

### 3. 추세 분석
- 시간에 따른 품질 변화 추적 (최근 30일)
- 품질 개선/저하 트렌드 감지
- 이전 세션과의 비교

## 사용 방법

### 방법 1: 독립 실행

```bash
# 기본 경로로 리포트 생성
python scripts/team_stats_aggregator.py

# 출력:
# [OK] Dashboard generated: RUNS/stats/team_dashboard.md
# [INFO] View report: cat RUNS/stats/team_dashboard.md
```

### 방법 2: Dev Assistant 통합

```bash
# dev_assistant를 통해 실행
python scripts/dev_assistant.py --team-stats

# 출력:
# ============================================================
# Team Statistics Dashboard Generated
# ============================================================
# Dashboard: RUNS/stats/team_dashboard.md
# Trends:    RUNS/stats/trends.json
# Problems:  RUNS/stats/problem_files.json
```

### 방법 3: 프로그래밍 방식

```python
from pathlib import Path
from scripts.team_stats_aggregator import TeamStatsAggregator

# 경로 설정
cache_dir = Path("RUNS/.cache")
evidence_dir = Path("RUNS/evidence")
output_dir = Path("RUNS/stats")

# Aggregator 생성
aggregator = TeamStatsAggregator(cache_dir, evidence_dir, output_dir)

# 리포트 생성
dashboard_path = aggregator.generate_report()
print(f"Dashboard: {dashboard_path}")
```

## 출력 파일

### 1. team_dashboard.md
팀 전체 품질 대시보드 (마크다운 형식)

**섹션**:
- Overview: 전체 통계 요약
- Quality Metrics: 상세 메트릭 테이블
- Quality Score Distribution: 점수 분포 차트
- Top Problem Files: 우선 수정 파일 목록
- Recommendations: 맞춤형 개선 제안

**예시**:
```markdown
# Team Code Quality Dashboard

**Generated**: 2025-10-23T00:21:56

## Overview
- **Total Files**: 10
- **Pass Rate**: 80.0%
- **Avg Quality Score**: 8.5/10.0

## Quality Score Distribution
```
9.0-10.0: ████████ (8)
 7.0-8.9: ██ (2)
 5.0-6.9:  (0)
```

### 2. trends.json
추세 분석 데이터 (JSON 형식)

```json
[
  {
    "timestamp": "2025-10-23T00:21:56",
    "quality_score": 8.5,
    "violation_count": 10,
    "security_issue_count": 2,
    "pass_rate": 80.0
  }
]
```

### 3. problem_files.json
문제 파일 상세 목록 (JSON 형식, 최대 20개)

```json
[
  {
    "file_path": "scripts/bad_file.py",
    "avg_quality_score": 4.5,
    "total_violations": 15,
    "total_security_issues": 3,
    "total_solid_violations": 5,
    "passed_checks": 0,
    "failed_checks": 3
  }
]
```

## 대시보드 해석

### 통과율 (Pass Rate)
- **90%+**: 우수 (녹색)
- **80-89%**: 양호 (노란색)
- **70-79%**: 주의 (주황색)
- **<70%**: 개선 필요 (빨간색)

### 품질 점수 (Quality Score)
- **9.0-10.0**: 우수한 코드
- **7.0-8.9**: 양호한 코드 (사소한 개선 필요)
- **5.0-6.9**: 보통 (여러 이슈 해결 필요)
- **3.0-4.9**: 낮음 (리팩토링 필요)
- **0.0-2.9**: 매우 낮음 (즉시 조치 필요)

### 권장사항 우선순위
1. **보안 이슈** (🛡️): 즉시 수정 (최우선)
2. **SOLID 위반** (🏗️): 리팩토링 계획
3. **통과율** (⚠️): 실패 파일 우선 처리
4. **품질 점수** (📊): 코드 품질 개선

## 추세 분석

### 품질 개선 확인
```bash
# 리포트를 여러 번 실행
python scripts/team_stats_aggregator.py

# trends.json에서 추세 확인
cat RUNS/stats/trends.json
```

### 트렌드 해석
- **improving**: 품질 점수 상승 ↑
- **declining**: 품질 점수 하락 ↓
- **stable**: 변화 없음 →

## 통합 워크플로우

### 매일 체크인
```bash
# 1. 캐시 통계 확인
python scripts/dev_assistant.py --cache-stats

# 2. 팀 통계 생성
python scripts/dev_assistant.py --team-stats

# 3. 대시보드 확인
cat RUNS/stats/team_dashboard.md

# 4. 문제 파일 처리
# problem_files.json 상위 파일부터 수정
```

### CI/CD 통합
```yaml
# .github/workflows/quality-check.yml
- name: Generate Team Stats
  run: python scripts/team_stats_aggregator.py

- name: Upload Dashboard
  uses: actions/upload-artifact@v3
  with:
    name: team-dashboard
    path: RUNS/stats/team_dashboard.md
```

## 고급 사용법

### 맞춤형 통계
```python
from scripts.team_stats_aggregator import StatsCollector

collector = StatsCollector(cache_dir, evidence_dir)
file_stats = collector.collect_file_stats()

# 특정 디렉토리만 필터링
scripts_stats = {
    k: v for k, v in file_stats.items()
    if k.startswith("scripts/")
}

team_stats = collector.collect_team_stats(scripts_stats)
print(f"Scripts avg quality: {team_stats.avg_quality_score:.1f}")
```

### 커스텀 대시보드
```python
from scripts.team_stats_aggregator import DashboardGenerator

generator = DashboardGenerator(output_dir)

# 상위 5개 문제 파일만
dashboard_path = generator.generate_dashboard(
    team_stats,
    file_stats,
    problem_files[:5]
)
```

## 문제 해결

### Q: "Cache file not found" 에러
A: 먼저 dev_assistant를 실행하여 캐시를 생성하세요:
```bash
python scripts/dev_assistant.py
# 파일을 몇 개 수정하고 저장
# Ctrl+C로 종료
python scripts/team_stats_aggregator.py
```

### Q: 통계가 부정확함
A: 캐시를 클리어하고 다시 시작:
```bash
python scripts/dev_assistant.py --clear-cache
python scripts/dev_assistant.py
# 파일 수정 후 재생성
```

### Q: 대시보드가 생성되지 않음
A: 로그 확인:
```bash
python scripts/team_stats_aggregator.py 2>&1 | tee stats.log
```

## 성능 특성

- **통계 수집**: <100ms (파일 100개 기준)
- **대시보드 생성**: <50ms
- **추세 분석**: <10ms
- **메모리 사용량**: <10MB

## 베스트 프랙티스

1. **정기적 실행**: 매일 또는 매주 실행하여 추세 파악
2. **문제 우선순위**: problem_files.json 상위부터 처리
3. **목표 설정**: 팀 평균 품질 점수 7.0+ 목표
4. **지속적 개선**: 매주 +0.5점 개선 목표
5. **보안 우선**: 보안 이슈는 즉시 수정

## 참고 문서

- [Phase C Week 1 구현](../PHASE_C_WEEK_1_IMPLEMENTATION.md)
- [Deep Analyzer 가이드](./DEEP_ANALYZER_GUIDE.md)
- [Verification Cache](../scripts/verification_cache.py)
- [테스트 코드](../tests/test_team_stats_aggregator.py)

## 요약

TeamStatsAggregator는:
- ✅ 28개 테스트 100% 통과
- ✅ 팀 전체 품질 가시화
- ✅ 추세 분석 (30일)
- ✅ 우선순위 기반 개선 제안
- ✅ dev_assistant 완전 통합
- ✅ <100ms 빠른 성능

코드 품질을 지속적으로 모니터링하고 개선하세요!
