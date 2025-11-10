# GitHub Template 활성화 가이드

**대상**: Repository 소유자 (positivef/dev-rules-starter-kit)
**소요 시간**: 2분
**목적**: GitHub Template 기능 활성화로 One-Click 프로젝트 생성 지원

---

## ✅ 전제 조건

- [ ] GitHub 저장소 소유자 권한
- [ ] 저장소가 Public 또는 GitHub Pro 계정 (Private template 허용)
- [ ] README.md, LICENSE, .gitignore 파일 존재

---

## 🚀 활성화 방법

### Step 1: Repository Settings 접근

1. GitHub 저장소 페이지로 이동:
   ```
   https://github.com/positivef/dev-rules-starter-kit
   ```

2. 상단 탭에서 **Settings** 클릭

### Step 2: Template 기능 활성화

1. Settings 페이지에서 **General** 섹션 찾기 (기본 페이지)

2. 페이지 상단 **"Template repository"** 섹션 찾기

3. **"Template repository"** 체크박스 선택

   ```
   ☑ Template repository

   Template repositories let users generate new repositories
   with the same directory structure and files.
   ```

4. **자동 저장됨** - 별도 저장 버튼 없음

### Step 3: 확인

1. 저장소 메인 페이지로 돌아가기

2. 우측 상단에 **"Use this template"** 버튼 표시 확인

   ```
   [Use this template ▼]
   ```

3. 드롭다운 메뉴 확인:
   - Create a new repository
   - Open in a codespace

---

## 🎯 활성화 후 사용자 경험

### 사용자 Workflow

1. **"Use this template"** 클릭
2. **"Create a new repository"** 선택
3. 새 저장소 정보 입력:
   - Repository name: `my-awesome-project`
   - Description: (선택)
   - Public/Private 선택
4. **"Create repository from template"** 클릭
5. 즉시 복사본 생성 (Fork 아님, 완전한 새 프로젝트)

### Fork vs Template 차이

| Feature | Fork | Template |
|---------|------|----------|
| 용도 | 기여 (Contribute) | 새 프로젝트 시작 |
| Git 히스토리 | 원본 포함 | 클린 시작 (히스토리 없음) |
| 원본 링크 | 표시됨 | 표시 안 됨 |
| 업데이트 | Sync 가능 | 독립적 |

**Template 장점**: 사용자가 완전히 독립적인 새 프로젝트 시작 가능

---

## 📋 체크리스트

활성화 후 확인사항:

- [ ] "Use this template" 버튼 표시됨
- [ ] README.md에 Template 안내 포함 (이미 완료)
- [ ] `scripts/setup_new_project.py` 실행 가능
- [ ] `docs/TEMPLATE_CUSTOMIZATION.md` 문서화 완료
- [ ] LICENSE 파일 존재 (MIT)
- [ ] .gitignore 적절히 설정됨

---

## 🔧 문제 해결

### "Use this template" 버튼이 안 보여요

**원인 1**: Template repository 체크박스 미선택
- Settings → General → Template repository 확인

**원인 2**: 저장소가 Private + GitHub Free 계정
- GitHub Pro 계정 필요
- 또는 Public 저장소로 변경

**원인 3**: 캐시 문제
- 브라우저 새로고침 (Ctrl+F5)
- 다른 브라우저에서 확인

### Template 생성 시 파일이 누락돼요

**원인**: .gitignore에 필수 파일 포함됨

**확인**:
```bash
# .gitignore 검토
cat .gitignore

# 포함되어야 하는 파일:
# - scripts/*.py (실행 스크립트)
# - config/*.yaml (Constitution)
# - docs/*.md (문서)
# - requirements.txt (의존성)
```

**제외되어야 하는 파일/폴더**:
```gitignore
# Correct exclusions
.venv/
__pycache__/
*.pyc
.env
RUNS/
```

---

## 🎨 커스터마이징 (선택사항)

### Template 설명 추가

Repository Description에 추가:
```
Constitution-based development framework with 95% automation.
Use this template to start your project in 5 minutes.
```

### Topics 태그 추가

Settings → General → Topics 섹션:
```
constitution-based, development-framework, automation,
python, yaml, obsidian, ci-cd, git-hooks, template
```

### Social Preview 이미지

Settings → General → Social preview:
- 1280x640 이미지 업로드
- Constitution 로고 또는 프레임워크 다이어그램

---

## 📊 성공 메트릭

Template 활성화 후 추적:

- **사용 횟수**: GitHub Insights → Traffic → Clone/Fork 통계
- **Star 수**: 사용자 관심도 측정
- **Issue/PR**: 커뮤니티 참여도
- **Setup script 실행**: 로그 수집 (선택)

**목표 (Stage 6 Phase 3)**:
- 첫 달: 10 uses
- 3개월: 50 uses
- 1년: 200 uses

---

## ✅ 완료 확인

다음 명령으로 Template 정상 작동 확인:

```bash
# 1. 다른 계정 또는 Incognito 모드에서
# 2. "Use this template" 클릭
# 3. 새 저장소 생성
# 4. Clone 후 setup script 실행

git clone https://github.com/YOUR_USERNAME/new-project.git
cd new-project
python scripts/setup_new_project.py

# 5. 출력 확인:
# [SUCCESS] Project setup complete!
```

---

**작성자**: AI (Claude) with VibeCoding Enhanced
**Stage**: 6 (Scale) - Phase 1 (Template Packaging)
**버전**: 1.0.0
**마지막 업데이트**: 2025-11-08
