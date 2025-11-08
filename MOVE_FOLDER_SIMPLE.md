# ✅ 폴더 이동 간단 가이드

## 🎯 맞습니다! 이 방법이 정확합니다

### 📁 전체 과정 (Windows 탐색기 + 명령어)

#### Step 1: 폴더 전체 이동 (잘라내기/붙여넣기)
```
Windows 탐색기에서:
1. 프로젝트 폴더 우클릭 → 잘라내기 (Ctrl+X)
2. 원하는 위치로 이동 → 붙여넣기 (Ctrl+V)

예시:
C:\temp\my-project → D:\Projects\my-project
```

#### Step 2: 이동한 폴더에서 가상환경 삭제
```bash
# 이동한 폴더로 이동
cd D:\Projects\my-project

# 기존 가상환경 삭제
rmdir /s /q .venv
# 또는 Windows 탐색기에서 .venv 폴더 삭제
```

#### Step 3: 새 가상환경 생성
```bash
# 같은 위치에서
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 🚀 한 번에 실행하는 명령어

```bash
# 폴더 이동 후 실행
cd D:\새위치\my-project
rmdir /s /q .venv && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt
```

## 📊 이동 가능/불가능 요소

| 항목 | 이동 가능? | 이유 |
|------|-----------|------|
| **scripts/** | ✅ 가능 | 상대 경로 사용 |
| **dashboards/** | ✅ 가능 | 상대 경로 사용 |
| **src/** | ✅ 가능 | 소스 코드 |
| **config/** | ✅ 가능 | 설정 파일 |
| **requirements.txt** | ✅ 가능 | 패키지 목록 |
| **.venv/** | ❌ 불가능 | 절대 경로 저장 |

## 💡 실제 예시

### 시나리오: C드라이브 용량 부족 → D드라이브로 이동

```bash
# 1. Windows 탐색기
C:\Users\user\my-project 폴더 잘라내기 (Ctrl+X)
D:\Development\ 에 붙여넣기 (Ctrl+V)

# 2. CMD 또는 PowerShell
cd D:\Development\my-project

# 3. 가상환경 재생성
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\activate

# 4. 패키지 재설치 (1-2분)
pip install -r requirements.txt

# 5. 테스트
python src\app.py
```

## ⚡ 빠른 팁

### 가상환경 폴더 확인
```bash
# .venv 폴더가 있는지 확인
dir .venv
# 있으면 삭제, 없으면 바로 생성
```

### 삭제 확인 메시지 없애기
```bash
# /q 옵션: 조용히(Quiet) 삭제
rmdir /s /q .venv

# /s: 하위 폴더 포함
# /q: 확인 메시지 없이
```

### 설치 시간 단축
```bash
# 핵심 패키지만 먼저
pip install flask streamlit pandas

# 나머지는 나중에
pip install -r requirements.txt
```

## ✅ 체크리스트

- [ ] 폴더 전체 이동 완료 (잘라내기/붙여넣기)
- [ ] 새 위치에서 CMD/PowerShell 열기
- [ ] `rmdir /s /q .venv` 실행
- [ ] `python -m venv .venv` 실행
- [ ] `.venv\Scripts\activate` 실행
- [ ] `pip install -r requirements.txt` 실행
- [ ] `python src\app.py` 테스트

## 🎉 완료!

**이제 새 위치에서 모든 기능을 사용할 수 있습니다!**

### 추가 질문 답변

**Q: 가상환경 활성화 상태에서 이동해도 되나요?**
A: 안됩니다. 먼저 `deactivate` 하고 이동하세요.

**Q: .venv 폴더가 안 보여요**
A: 숨김 파일 보기 설정 필요 (탐색기 → 보기 → 숨김 항목 체크)

**Q: 이동 후 Git이 이상해요**
A: Git은 문제없음. `.git` 폴더는 이동 가능합니다.

---
**핵심**: 폴더 이동은 자유! 단, .venv만 재생성하면 됩니다!
