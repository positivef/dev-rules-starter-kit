# Team Code Quality Dashboard

**Generated**: 2025-10-30T07:06:00.184621

## Overview

- **Total Files**: 170
- **Total Checks**: 170
- **Pass Rate**: 62.9%
- **Avg Quality Score**: 8.8/10.0
- **Cache Hit Rate**: 100.0%

## Quality Metrics

| Metric | Count |
|--------|-------|
| Passed Checks | 107 |
| Failed Checks | 63 |
| Total Violations | 311 |
| Security Issues | 28 |
| SOLID Violations | 279 |

## Quality Score Distribution

```
9.0-10.0: ████████████████████████████████████████████████████████████████████████████████████████████ (92)
 7.0-8.9: ████████████████████████████████████████████████████████████████████ (68)
 5.0-6.9: ██████████ (10)
 3.0-4.9:  (0)
 0.0-2.9:  (0)
```

## Top Problem Files

| File | Quality | Violations | Security | SOLID | Status |
|------|---------|------------|----------|-------|--------|
| session_analyzer.py | 5.0 | 14 | 0 | 10 | ❌ FAIL |
| test_deep_analyzer.py | 5.0 | 0 | 14 | 0 | ✅ PASS |
| test_phase_c_week2_integration.py | 5.7 | 0 | 3 | 2 | ✅ PASS |
| task_executor.py | 5.8 | 12 | 0 | 4 | ❌ FAIL |
| framework_validator.py | 5.8 | 6 | 0 | 8 | ❌ FAIL |
| test_error_learner.py | 5.9 | 0 | 5 | 0 | ✅ PASS |
| session_report_scheduler.py | 6.0 | 5 | 0 | 9 | ❌ FAIL |
| final_validation.py | 6.0 | 5 | 0 | 6 | ❌ FAIL |
| safe_token_optimizer.py | 6.2 | 4 | 0 | 7 | ❌ FAIL |
| team_stats_aggregator.py | 6.8 | 1 | 0 | 6 | ❌ FAIL |

## Recommendations

- 🛡️ **Security**: 28개의 보안 이슈 발견. 즉시 수정 필요.
- 🏗️ **Architecture**: 279개의 SOLID 위반. 리팩토링 고려.
- ⚠️ **Pass Rate**: 62.9% (목표 80%+). 실패한 파일 우선 수정.
- 🎯 **Priority**: `session_analyzer.py` 파일부터 시작 (Quality 5.0)
