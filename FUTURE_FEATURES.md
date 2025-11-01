# Future Features Roadmap

## Course Generator (강의 자동 생성 시스템)

**Priority**: Medium
**Status**: Planned
**Added**: 2025-11-01

### Overview
Obsidian 개발일지의 태그와 레슨앤런을 활용하여 강의 콘텐츠를 자동 생성하는 시스템

### Core Features

#### 1. Content Extraction
- Dataview 쿼리로 태그 기반 개발일지 필터링
- 시행착오 패턴 추출 (문제 → 시도 → 해결 → 교훈)
- 시간순 학습 경로 자동 구성

#### 2. Course Structure Generation
```python
# scripts/course_generator.py
def generate_course_from_tags(tag_filter: str, output_dir: str):
    """
    태그로 필터링한 개발일지를 강의 자료로 변환

    Args:
        tag_filter: "domain/testing" 등
        output_dir: "courses/pytest-mastery/"
    """
    # 1. Dataview 쿼리로 관련 파일 수집
    devlogs = query_obsidian_by_tag(tag_filter)

    # 2. 시간순 정렬 → 학습 경로 추출
    learning_path = extract_learning_progression(devlogs)

    # 3. 시행착오 → 레슨 변환
    lessons = convert_failures_to_lessons(devlogs)

    # 4. 강의 모듈 생성
    modules = group_into_modules(lessons, by="phase")

    # 5. 슬라이드/튜토리얼/스크립트 생성
    for module in modules:
        generate_slides(module, f"{output_dir}/slides/")
        generate_tutorial(module, f"{output_dir}/tutorials/")
        generate_video_script(module, f"{output_dir}/scripts/")

    # 6. 커리큘럼 인덱스 생성
    generate_curriculum_index(modules, f"{output_dir}/README.md")
```

#### 3. Output Formats
- **슬라이드**: Reveal.js/Advanced Slides 형식
- **튜토리얼**: 단계별 실습 가이드
- **영상 스크립트**: 타임스탬프 포함 스크립트
- **커리큘럼**: Dataview 기반 자동 인덱스

#### 4. Automation
- 개발일지 작성 → 강의 콘텐츠 자동 업데이트
- 태그 변경 시 관련 모듈 자동 재구성
- 통계/그래프 실시간 반영

### Technical Requirements

#### Dependencies
```bash
pip install obsidian-export  # Obsidian → Markdown 변환
pip install marko             # Markdown 파싱
pip install jinja2            # 템플릿 엔진
```

#### Integration Points
- `scripts/auto_sync_obsidian.py` - YAML 메타데이터 활용
- `scripts/obsidian_bridge.py` - Obsidian API 연동
- Dataview queries - 콘텐츠 필터링

### Use Cases

#### Example 1: Testing Course
```bash
python scripts/course_generator.py \
  --tag "domain/testing" \
  --output "courses/pytest-mastery" \
  --format slides,tutorial,script
```

**Output**:
```
courses/pytest-mastery/
├── README.md (커리큘럼)
├── modules/
│   ├── 01-basics.md
│   ├── 02-advanced.md
│   └── 03-performance.md
├── slides/ (Reveal.js)
├── tutorials/ (실습 가이드)
└── scripts/ (영상 스크립트)
```

#### Example 2: Multi-topic Course
```bash
python scripts/course_generator.py \
  --tags "domain/backend,domain/testing" \
  --project "q1-2026" \
  --output "courses/backend-testing-mastery"
```

### Benefits

1. **자동화**: 개발하면서 강의 콘텐츠 자동 축적
2. **검증된 내용**: 실제 프로젝트 경험 기반 (작동 보증)
3. **일관성**: 템플릿 기반 표준화된 구조
4. **시간 절약**: 강의 제작 시간 70% 단축
5. **지속 업데이트**: 개발일지 수정 시 강의도 자동 반영

### Implementation Plan

#### Phase 1: Core Engine (1-2 days)
- [ ] Obsidian YAML 파싱
- [ ] 태그 필터링 쿼리
- [ ] 레슨 추출 로직

#### Phase 2: Content Generation (2-3 days)
- [ ] 슬라이드 템플릿
- [ ] 튜토리얼 템플릿
- [ ] 스크립트 템플릿

#### Phase 3: Automation (1-2 days)
- [ ] Git hook 통합
- [ ] 자동 업데이트 로직
- [ ] CI/CD 파이프라인

#### Phase 4: Enhancement (Optional)
- [ ] Obsidian Publish 연동
- [ ] MkDocs 변환
- [ ] 통계/그래프 시각화

### Related Documentation
- [OBSIDIAN_DATAVIEW_GUIDE.md](docs/OBSIDIAN_DATAVIEW_GUIDE.md) - Dataview 쿼리 활용
- [OBSIDIAN_PRACTICAL_GUIDE.md](docs/OBSIDIAN_PRACTICAL_GUIDE.md) - 실전 사용 패턴

---

**Note**: 이 기능은 현재 Obsidian Dataview 통합이 완료된 상태에서 추가 가능한 확장 기능입니다. 구현 시 기존 개발일지 시스템과 완전히 호환됩니다.
