# 📦 패키지는 어디에 설치되나요?

## 🎯 핵심: 패키지는 .venv 폴더 안에 설치됩니다!

### 📁 패키지 설치 위치

```
my-project/
├── .venv/                    # 🔴 여기에 모든 패키지가 설치됨!
│   ├── Lib/
│   │   └── site-packages/    # 🔴 Flask, Streamlit 등 모든 패키지
│   │       ├── flask/
│   │       ├── streamlit/
│   │       ├── pandas/
│   │       └── ... (모든 설치된 패키지)
│   └── Scripts/
│       ├── python.exe
│       └── pip.exe
├── scripts/                  # ✅ 소스 코드 (이동 가능)
├── src/                      # ✅ 소스 코드 (이동 가능)
└── requirements.txt          # ✅ 패키지 목록 (이동 가능)
```

## ❓ 왜 다시 설치해야 하나요?

### .venv 삭제 = 패키지도 삭제

```bash
rmdir /s /q .venv  # 이 명령은 다음을 삭제합니다:
                   # - Python 실행 환경
                   # - pip
                   # - 설치했던 모든 패키지 (Flask, Streamlit 등)
```

### 비유로 설명
```
.venv = 냉장고
패키지 = 냉장고 안의 음식

냉장고를 버리면 → 음식도 함께 버려짐
새 냉장고 사면 → 음식도 다시 사야 함
```

## 📊 무엇이 삭제되고 무엇이 남나요?

| 항목 | .venv 삭제 시 | 설명 |
|------|-------------|------|
| **Flask, Streamlit 등** | ❌ 삭제됨 | .venv/Lib/site-packages에 있음 |
| **pip 자체** | ❌ 삭제됨 | .venv/Scripts/pip.exe |
| **Python 인터프리터** | ❌ 삭제됨 | .venv/Scripts/python.exe |
| **requirements.txt** | ✅ 남음 | 프로젝트 폴더에 있음 |
| **소스 코드** | ✅ 남음 | scripts/, src/ 등 |

## 🔍 확인해보기

### 패키지가 어디 있는지 확인
```bash
# 가상환경 활성화 후
.venv\Scripts\activate

# pip로 설치 위치 확인
pip show flask

# 결과:
Location: c:\my-project\.venv\lib\site-packages  # .venv 안에 있음!
```

### .venv 폴더 크기 확인
```bash
# .venv 폴더 크기 확인 (보통 100-500MB)
dir .venv

# 패키지가 많으면 1GB 이상도 가능
# 이 모든 것이 .venv 삭제 시 사라짐
```

## ✅ 그래서 결론

```bash
# 1. 폴더 이동 후
cd D:\new-location\my-project

# 2. .venv 삭제 (= 패키지도 삭제)
rmdir /s /q .venv

# 3. 새 .venv 생성 (= 빈 가상환경)
python -m venv .venv

# 4. 패키지 재설치 필요! (requirements.txt 참조)
.venv\Scripts\activate
pip install -r requirements.txt  # 다시 설치해야 함!
```

## 💡 자주 하는 오해

### ❌ 잘못된 생각
"패키지를 설치하면 프로젝트 폴더에 설치되는 거 아니야?"

### ✅ 올바른 이해
"패키지는 .venv/Lib/site-packages/ 안에 설치됨"

### ❌ 잘못된 생각
"requirements.txt가 있으면 패키지도 있는 거 아니야?"

### ✅ 올바른 이해
"requirements.txt는 쇼핑 목록, 실제 패키지는 .venv 안에"

## 🚀 시간 절약 팁

### 설치 시간이 아까우면?
```bash
# 옵션 1: 가상환경째로 복사 (비추천, 경로 문제)
xcopy /E /I .venv D:\backup\.venv_backup

# 옵션 2: 캐시 활용 (추천)
pip install --cache-dir D:\pip-cache -r requirements.txt
# 다음 번엔 캐시에서 빠르게 설치

# 옵션 3: 핵심 패키지만 먼저
pip install flask streamlit  # 필수만 먼저
# 나머지는 나중에
```

## 📝 한 줄 정리

> **".venv 폴더 = 패키지 저장소"**
>
> .venv 삭제 = 패키지 삭제 = 재설치 필요!

---
**requirements.txt**는 레시피, **패키지**는 실제 재료입니다.
레시피는 남아있어도, 재료는 다시 사야 합니다!
