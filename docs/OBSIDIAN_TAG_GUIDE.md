# Obsidian Tagging Guidelines

## 목적
개발 일지와 교훈 문서를 Obsidian에서 일관된 태그 체계로 관리하여, 세컨드 브레인에서 필요한 정보를 빠르게 찾을 수 있도록 합니다.

## 기본 규칙
- 모든 개발 일지 파일명은 `YYYY-MM-DD_<프로젝트>_<키워드>.md`
- 문서 상단에 다음과 같이 키워드 태그를 추가합니다.
  ```markdown
  #devlog #프로젝트명 #주요주제
  ```
- 주요 프로젝트별 태그 예시
  - `#DevRulesStarter`, `#DoubleDiver`, `#PromptCompression`
- 시행착오/교훈 문서는 `#lesson`, 프롬프트 관련은 `#prompt_feedback` 태그를 포함합니다.

## 활용
- Obsidian 검색에서 `tag:#devlog tag:#DevRulesStarter` 등으로 필터링해 빠르게 문서를 찾습니다.
- Slack 리포트에서 태그 정보가 필요하면 해당 문서 링크를 공유해 추적성을 확보합니다.

## 추후 확장
- 프로젝트가 증가하면 태그 목록을 `docs/OBSIDIAN_TAG_GUIDE.md`에 갱신하여 팀원/AI가 동일 규칙을 따르도록 합니다.
