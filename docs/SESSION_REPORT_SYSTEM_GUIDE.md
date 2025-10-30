# Session Report System Guide

## 개요

Session Report System은 SessionManager의 데이터를 분석하여 주기적으로 리포트를 생성하고 팀과 공유할 수 있는 자동화 시스템입니다.

## 주요 기능

### 1. 다양한 리포트 형식
- **HTML**: 웹 브라우저에서 보기 좋은 시각적 리포트
- **PDF**: 인쇄 및 공유용 (matplotlib 필요)
- **JSON**: 프로그래밍적 분석용
- **CSV**: Excel에서 열기
- **Excel**: 다중 시트 분석 (pandas 필요)

### 2. 자동 스케줄링
- 일일/주간/월간 자동 리포트 생성
- Windows Task Scheduler 통합
- Linux/Mac cron 지원
- 백그라운드 실행

### 3. 리포트 배포
- 이메일 자동 전송
- Slack 알림
- 로컬 저장

## 설치

### 필수 패키지
```bash
# 기본 기능
pip install jinja2  # HTML 템플릿 (선택적)

# 추가 기능
pip install matplotlib  # PDF 리포트
pip install pandas openpyxl  # Excel 내보내기
pip install schedule  # 백그라운드 스케줄링
```

## 사용 방법

### 1. 수동 리포트 생성

#### HTML 리포트
```bash
python scripts/session_report_generator.py --format html
```

#### PDF 리포트
```bash
python scripts/session_report_generator.py --format pdf
```

#### JSON 리포트
```bash
python scripts/session_report_generator.py --format json
```

#### CSV 내보내기
```bash
python scripts/session_report_generator.py --export csv
```

#### Excel 내보내기
```bash
python scripts/session_report_generator.py --export excel
```

### 2. 기간 설정

```bash
# 일일 리포트
python scripts/session_report_generator.py --period daily

# 주간 리포트 (기본값)
python scripts/session_report_generator.py --period weekly

# 월간 리포트
python scripts/session_report_generator.py --period monthly

# 사용자 정의 기간
python scripts/session_report_generator.py --period custom --days 14
```

### 3. 자동 스케줄링

#### 단일 실행
```bash
# 주간 리포트 즉시 생성
python scripts/session_report_scheduler.py --run-once --period weekly
```

#### 백그라운드 스케줄러
```bash
# 설정된 스케줄에 따라 계속 실행
python scripts/session_report_scheduler.py --schedule weekly

# 모든 스케줄 활성화
python scripts/session_report_scheduler.py --schedule all
```

#### Windows Task Scheduler 설정
```bash
# Windows 작업 스케줄러에 등록
python scripts/session_report_scheduler.py --setup-windows-task
```

#### Linux/Mac cron 설정
```bash
# cron 설정 명령 표시
python scripts/session_report_scheduler.py --setup-cron

# crontab -e 에 다음 추가:
0 9 * * 1 /usr/bin/python3 /path/to/session_report_scheduler.py --run-once --period weekly
```

## 설정 파일

### config/report_scheduler.json
```json
{
  "enabled": true,
  "schedules": {
    "daily": {
      "enabled": false,
      "time": "09:00",
      "format": "html",
      "send_email": false,
      "send_slack": false
    },
    "weekly": {
      "enabled": true,
      "day": "monday",
      "time": "09:00",
      "format": "html",
      "send_email": false,
      "send_slack": true
    },
    "monthly": {
      "enabled": false,
      "day": 1,
      "time": "09:00",
      "format": "pdf",
      "send_email": true,
      "send_slack": true
    }
  },
  "email": {
    "enabled": false,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "from_email": "your-email@gmail.com",
    "from_password": "your-app-password",
    "to_emails": ["recipient1@example.com", "recipient2@example.com"],
    "use_tls": true
  },
  "slack": {
    "enabled": false,
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  }
}
```

## 리포트 내용

### 실행 통계
- 총 작업 수
- 성공/실패 카운트
- 성공률
- 총 실행 시간
- 평균 실행 시간

### 작업 패턴
- 자주 실행한 작업 TOP 10
- 자주 실패한 작업
- 작업별 평균 실행 시간
- 명령어 사용 패턴

### 생산성 분석
- 시간대별 활동 분포
- 요일별 활동 패턴
- 평균 세션 시간
- 가장 생산적인 시간대

### 에러 분석
- 반복되는 에러 패턴
- 에러별 작업 매핑
- 에러 타임라인

### 인사이트
- 자동 생성된 개선 제안
- 주의사항 및 경고
- 긍정적 패턴 식별

## HTML 리포트 예시

```html
┌─────────────────────────────────────────────────┐
│          Session Management Report              │
│         Period: Weekly | Duration: 7 days       │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌────────┬────────┬────────┬────────┐        │
│  │  156   │  142   │   14   │ 91.0%  │        │
│  │ Total  │Success │Failed  │Success │        │
│  │ Tasks  │        │        │  Rate  │        │
│  └────────┴────────┴────────┴────────┘        │
│                                                 │
│  Most Frequent Tasks:                          │
│  • TEST-2025-10: 45 executions                 │
│  • FEAT-2025-10: 32 executions                 │
│  • FIX-2025-10: 28 executions                  │
│                                                 │
│  Productivity Insights:                        │
│  • Average Session: 85 minutes                 │
│  • Peak Hours: 9:00, 14:00, 20:00             │
│                                                 │
│  Recommendations:                              │
│  💡 Work during morning hours for best focus   │
│  ⚠️ FIX-DB task fails frequently - investigate │
│  ✅ Success rate above 90% - excellent!        │
│                                                 │
└─────────────────────────────────────────────────┘
```

## 이메일 설정

### Gmail 사용 시
1. 2단계 인증 활성화
2. 앱 비밀번호 생성
3. config에 앱 비밀번호 입력

### Outlook 사용 시
```json
"smtp_server": "smtp.office365.com",
"smtp_port": 587
```

## Slack 설정

1. Slack Workspace에서 Incoming Webhook 생성
2. Webhook URL 복사
3. config에 URL 입력

## 테스트

### 전체 테스트
```bash
# 자동 테스트 스위트
python scripts/test_report_system.py --auto

# 대화형 메뉴
python scripts/test_report_system.py --interactive
```

### 테스트 메뉴
```
1. Generate sample data - 샘플 데이터 생성
2. Test report generation - 리포트 생성 테스트
3. Test scheduler - 스케줄러 테스트
4. Generate all report formats - 모든 형식 생성
5. Show generated reports - 생성된 리포트 표시
6. Run full test suite - 전체 테스트 실행
```

## 출력 디렉토리

```
RUNS/reports/
├── session_report_daily_*.html
├── session_report_weekly_*.html
├── session_report_monthly_*.html
├── session_report_*.pdf
├── session_report_*.json
├── session_data_*.csv
├── session_data_*.xlsx
└── last_run.json
```

## 트러블슈팅

### matplotlib 설치 오류
```bash
# Windows
pip install matplotlib --no-cache-dir

# Linux
sudo apt-get install python3-tk
pip install matplotlib
```

### pandas 설치 오류
```bash
pip install pandas openpyxl
```

### schedule 설치
```bash
pip install schedule
```

### 이메일 전송 실패
- 앱 비밀번호 확인
- 보안 설정 확인
- 방화벽 확인

### Slack 알림 실패
- Webhook URL 유효성 확인
- 네트워크 연결 확인

## 성능 고려사항

- **리포트 생성**: <5초 (100 세션)
- **PDF 생성**: <10초 (차트 포함)
- **이메일 전송**: <5초
- **메모리 사용**: <100MB

## 향후 개선 계획

1. **대시보드 통합**: 리포트를 대시보드에서 직접 보기
2. **비교 분석**: 기간별 비교 리포트
3. **커스텀 템플릿**: 사용자 정의 리포트 템플릿
4. **API 엔드포인트**: RESTful API로 리포트 제공
5. **클라우드 저장소**: AWS S3, Google Drive 연동

## 결론

Session Report System은 개발 생산성을 정기적으로 추적하고 분석할 수 있는 강력한 자동화 도구입니다. 다양한 형식의 리포트를 생성하고 자동으로 팀과 공유할 수 있어 지속적인 개선이 가능합니다.
