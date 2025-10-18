
# 새 프로젝트 개발 가이드 (feat. Dev-Rules Starter Kit)

이 문서는 `dev-rules-starter-kit`를 사용하여 새로운 프로젝트를 시작하고, 표준화된 개발 워크플로우를 따라 개발을 진행하는 방법을 안내합니다.

---

## Phase 1: 프로젝트 초기 설정 (5분)

단 5분 만에 모든 규칙이 적용된, 코딩 준비가 완료된 프로젝트를 생성합니다.

### Step 1: 스타터 킷 복사 및 프로젝트 생성

먼저, 이 스타터 킷을 로컬에 복제(`clone`)한 후, 새로 만들고 싶은 프로젝트의 디렉토리를 생성하고 그 안으로 스타터 킷 파일들을 복사합니다.

```bash
# 예시: "MyAwesomeAPI" 라는 새 프로젝트를 생성합니다.
mkdir MyAwesomeAPI
cd MyAwesomeAPI

# dev-rules-starter-kit의 모든 파일들을 새 프로젝트 디렉토리로 복사합니다.
# (경로는 실제 스타터 킷 위치에 맞게 수정해주세요)
cp -r path/to/dev-rules-starter-kit/* .
cp -r path/to/dev-rules-starter-kit/.* . 2>/dev/null || true
```

### Step 2: 자동 설정 스크립트 실행

`setup.py` 스크립트를 실행하여 프로젝트를 초기화합니다. 이 단계에서 프로젝트 이름이 파일 전체에 자동으로 적용되고, 프레임워크에 맞는 템플릿 파일들이 생성되며, 모든 개발 도구와 Git 훅이 설정됩니다.

```bash
# python setup.py --project-name [내 프로젝트명] --framework [사용할 프레임워크]
python setup.py --project-name "MyAwesomeAPI" --framework fastapi
```

*   `--project-name`: 필수. 생성할 프로젝트의 이름을 지정합니다.
*   `--framework`: 선택. `fastapi` 등 미리 정의된 프레임워크를 지정하면, 해당 프레임워크에 맞는 `Dockerfile`, `main.py` 등의 보일러플레이트 코드가 자동으로 생성됩니다.

스크립트가 성공적으로 실행되면, 이제 이 디렉토리는 `MyAwesomeAPI`를 위한 완벽한 개발 환경이 됩니다.

### Step 3: Git 저장소 초기화 및 첫 커밋

이제 모든 설정이 완료되었으므로, Git 저장소를 초기화하고 첫 커밋을 만듭니다.

```bash
# 1. Git 저장소 초기화
git init
git branch -m main

# 2. 모든 파일 추가
git add .

# 3. 첫 커밋 (이때 pre-commit 훅이 처음으로 실행됩니다!)
git commit -m "feat: initial project setup with dev-rules-starter-kit"
```

> **✨ 자동화의 시작**
> 첫 커밋 시, `pre-commit` 훅이 자동으로 실행되어 코드 스타일과 커밋 메시지 형식을 검사합니다. 만약 커밋 메시지가 "feat: ..." 와 같은 형식에 맞지 않으면 커밋이 실패합니다. 이것이 바로 "자동 규칙 강제 시스템"이 동작하는 첫 순간입니다.

---

## Phase 2: 일상적인 개발 워크플로우

프로젝트 설정이 완료되었으니, 이제 실제 개발을 진행하는 방법을 알아봅니다.

### 시나리오 A: 복잡한 새 기능 추가 (YAML 계약 방식)

여러 파일 수정, 여러 명령어 실행 등 복잡한 작업을 수행할 때 사용합니다. 모든 과정이 상세히 기록됩니다.

1.  **계약서 작성:** `TASKS/TEMPLATE.yaml` 파일을 복사하여 새 YAML 파일(예: `TASKS/FEAT-AddUserAuth.yaml`)을 만듭니다.
2.  **내용 수정:** `title`, `description`, `commands`, `evidence` 등 작업 내용을 명확히 기술합니다.
3.  **실행:** `task_executor.py`로 계약서를 실행합니다.
    ```bash
    # 계획 확인 (실행 전 검토)
    python scripts/task_executor.py TASKS/FEAT-AddUserAuth.yaml --plan

    # 실제 실행
    python scripts/task_executor.py TASKS/FEAT-AddUserAuth.yaml
    ```
4.  **결과:** 실행된 모든 명령어, 증거 파일 목록, 결과가 Obsidian에 자동으로 상세히 기록됩니다.

### 시나리오 B: 간단한 버그 수정 ("라이트 모드")

오타 수정, 단일 파일 변경 등 간단한 작업을 빠르게 기록할 때 사용합니다.

1.  **코드 수정:** 평소처럼 코드를 수정합니다.
2.  **라이트 모드 실행:** YAML 파일 없이 `task_executor.py`를 실행합니다.
    ```bash
    python scripts/task_executor.py
    ```
3.  **작업 요약 입력:** 스크립트가 물어보는 질문에 수행한 작업을 한 줄로 답변합니다.
    ```
    >> What did you accomplish? (e.g., fix: Corrected a typo in README): fix: main.py의 오타 수정
    ```
4.  **결과:** 변경된 파일 목록과 작업 요약이 Obsidian에 자동으로 기록됩니다. YAML 파일을 만들 필요가 없어 매우 편리합니다.

### 커밋 프로세스

작업이 완료되면 커밋을 만듭니다.

1.  `git add .`로 변경된 파일들을 스테이징합니다.
2.  `git commit -m "fix(api): handle null user exception"` 과 같이 Conventional Commits 형식에 맞춰 커밋 메시지를 작성합니다.
3.  커밋 시 `pre-commit` 훅이 자동으로 코드 품질과 메시지 형식을 검사합니다.
    *   **성공 시:** 커밋이 성공적으로 생성됩니다.
    *   **실패 시:** 오류 메시지가 표시됩니다. (예: `subject may not be empty`, `type must be one of [feat, fix, ...]` 등). 메시지에 따라 코드를 수정하거나 커밋 메시지를 `git commit --amend`로 수정하여 다시 커밋합니다.

---

## Phase 3: 프로젝트 구조 이해

이 스타터 킷이 생성한 주요 디렉토리와 파일의 역할은 다음과 같습니다.

*   `DEVELOPMENT_RULES.md`: 우리 프로젝트의 모든 개발 규칙(Git, 버전 관리, 문서 등)이 정의된 헌법과 같은 문서입니다.
*   `setup.py`: 프로젝트를 초기화하고 모든 자동화 설정을 담당하는 스크립트입니다.
*   `.pre-commit-config.yaml`: 커밋 시마다 실행될 자동 검사 규칙들이 정의된 파일입니다.
*   `scripts/`: `task_executor.py` 등 프로젝트 자동화를 위한 스크립트들이 위치합니다.
*   `TASKS/`: 복잡한 작업의 내용과 절차를 기록하는 YAML 계약서들이 저장되는 곳입니다.
*   `templates/`: `setup.py`가 프로젝트 생성 시 참조하는 프레임워크별 템플릿 파일들이 들어있습니다.

---

## 결론

이 가이드를 따라 개발을 진행하면, 모든 팀원이 일관된 규칙을 따르게 되어 코드 품질이 향상되고, 모든 작업이 기록으로 남아 추적성이 높아집니다. 이 자동화된 워크플로우를 적극적으로 활용하여 더 효율적이고 안정적인 개발을 경험해 보세요.
