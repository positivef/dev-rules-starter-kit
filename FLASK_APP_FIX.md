# 🔧 Flask 웹앱 버튼 작동 문제 해결

## 🚨 문제
"페이지는 표시되는데 버튼 클릭이 안 돼요"

## ✅ 해결책: 작동하는 Flask 앱 생성

### Step 1: 새로운 Flask 앱 파일 복사
```bash
# flask_app.py 파일을 프로젝트의 src 폴더로 복사
copy flask_app.py "당신의프로젝트경로\src\app.py"

# 예시:
copy flask_app.py D:\my-project\src\app.py
```

### Step 2: Flask 앱 실행
```bash
# 프로젝트 폴더에서
cd D:\my-project

# 가상환경 활성화
.venv\Scripts\activate

# Flask 앱 실행
python src\app.py
```

### Step 3: 브라우저에서 확인
```
http://localhost:5000
```

## 🎯 새 Flask 앱의 기능

### 작동하는 버튼들:
1. **Run Code Analysis** - 코드 분석 실행 (클릭 가능!)
2. **Validate Constitution** - Constitution 검증 (클릭 가능!)
3. **Run Tests** - 테스트 실행 (클릭 가능!)
4. **Task Manager** - 작업 관리 페이지로 이동
5. **Analysis Dashboard** - 분석 대시보드로 이동

### 실시간 기능:
- 상태 자동 업데이트 (10초마다)
- API 응답 즉시 표시
- 결과 영역 동적 표시

## 📁 자동 생성되는 구조

Flask 앱 실행 시 자동으로 생성:
```
your-project/
├── src/
│   └── app.py        # Flask 메인 앱
├── templates/        # 자동 생성됨
│   ├── index.html    # 메인 페이지
│   ├── tasks.html    # 작업 관리
│   └── analysis.html # 분석 대시보드
└── static/           # 자동 생성됨
```

## 🔍 문제 진단

### 원인: 기존 템플릿에 JavaScript 없음
기존 Flask 앱은 HTML만 있고 JavaScript 이벤트 핸들러가 없어서 버튼이 작동하지 않았습니다.

### 해결: JavaScript 추가
새 Flask 앱은:
- 버튼에 `onclick` 이벤트 추가
- `fetch` API로 서버와 통신
- 동적으로 결과 표시

## 💡 추가 팁

### 포트 변경이 필요한 경우
```bash
# 포트 5001로 실행
PORT=5001 python src\app.py

# 또는 코드에서 직접 수정
# app.py 마지막 부분
port = int(os.environ.get('PORT', 5001))  # 5000 → 5001
```

### 디버그 모드 끄기
```bash
# 프로덕션 환경에서
set FLASK_DEBUG=False
python src\app.py
```

### 외부 접속 허용
```python
# app.py에서
app.run(host='0.0.0.0', port=5000)  # 모든 IP에서 접속 가능
```

## 🎉 확인 체크리스트

- [ ] flask_app.py를 src/app.py로 복사
- [ ] 가상환경 활성화 (.venv\Scripts\activate)
- [ ] python src\app.py 실행
- [ ] http://localhost:5000 접속
- [ ] 버튼 클릭 테스트
- [ ] 결과 표시 확인

## 📊 비교

| 기능 | 기존 앱 | 새 앱 |
|------|---------|-------|
| 페이지 표시 | ✅ | ✅ |
| 버튼 클릭 | ❌ | ✅ |
| API 통신 | ❌ | ✅ |
| 실시간 업데이트 | ❌ | ✅ |
| 자동 템플릿 생성 | ❌ | ✅ |

**이제 모든 버튼이 작동합니다!** 🎉
