# BenchmarkAnalyzer Design Document

**날짜**: 2025-11-04
**버전**: 1.0.0
**상태**: Design Phase
**목적**: 자동 경쟁사 벤치마킹 시스템 아키텍처 설계

---

## 📐 System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    BenchmarkAnalyzer                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  Competitor  │  │   Product    │  │ Differentiation │  │
│  │   Searcher   │→ │   Analyzer   │→ │   Generator     │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│         ↓                  ↓                    ↓          │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  WebSearch   │  │  WebFetch    │  │  YAML Builder   │  │
│  │  Integration │  │  Integration │  │                 │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │                   │                    │
         ↓                   ↓                    ↓
  ┌────────────┐      ┌────────────┐      ┌────────────┐
  │ Competitors│      │ Analysis   │      │  YAML      │
  │    List    │      │   Report   │      │  Section   │
  └────────────┘      └────────────┘      └────────────┘
```

### Components

#### 1. CompetitorSearcher
- **입력**: 검색 쿼리 (예: "todo app", "habit tracker")
- **출력**: 경쟁사 리스트 (3-5개)
- **역할**: WebSearch로 인기 제품 검색 및 순위 매김

#### 2. ProductAnalyzer
- **입력**: 경쟁사 제품 정보 (URL, GitHub repo)
- **출력**: 특장점/약점 분석 결과
- **역할**: README, docs, 리뷰 분석

#### 3. DifferentiationGenerator
- **입력**: 경쟁사 분석 결과 리스트
- **출력**: 차별화 전략 3개 이상
- **역할**: 갭 분석 및 차별화 포인트 도출

#### 4. YAMLBuilder
- **입력**: 전체 분석 결과
- **출력**: YAML benchmarking 섹션
- **역할**: 구조화된 YAML 포맷 생성

---

## 🔍 Detailed Component Design

### 1. CompetitorSearcher

```python
class CompetitorSearcher:
    """경쟁사 제품 검색 및 순위 매김"""

    def __init__(self, web_search_client):
        self.web_search = web_search_client
        self.ranking_weights = {
            "github_stars": 0.4,
            "recent_activity": 0.3,
            "documentation_quality": 0.2,
            "community_size": 0.1,
        }

    def search_competitors(
        self,
        query: str,
        category: str = "software",
        min_results: int = 3,
        max_results: int = 5
    ) -> List[Competitor]:
        """
        경쟁사 제품 검색

        Args:
            query: 검색어 (예: "todo app python")
            category: 카테고리 (software, library, plugin, etc.)
            min_results: 최소 결과 개수
            max_results: 최대 결과 개수

        Returns:
            Competitor 객체 리스트 (인기도순 정렬)

        Performance:
            - Target: <5분
            - WebSearch 호출: 3-5회
            - 캐싱: 24시간 TTL
        """
        # Search strategies
        search_queries = self._generate_search_queries(query, category)

        # Execute searches in parallel
        results = []
        for search_query in search_queries:
            search_results = self.web_search.search(search_query)
            results.extend(self._parse_search_results(search_results))

        # Deduplicate and rank
        unique_results = self._deduplicate(results)
        ranked = self._rank_by_popularity(unique_results)

        # Return top N
        return ranked[min_results:max_results]

    def _generate_search_queries(self, query: str, category: str) -> List[str]:
        """
        검색 쿼리 생성

        Examples:
            query="todo app" → [
                "best todo app 2025",
                "top todo app github",
                "popular todo app open source",
                "todo app most stars"
            ]
        """
        templates = [
            f"best {query} {datetime.now().year}",
            f"top {query} github",
            f"popular {query} open source",
            f"{query} most stars",
            f"{query} highly rated"
        ]
        return templates[:3]  # Top 3 queries

    def _rank_by_popularity(self, competitors: List[Competitor]) -> List[Competitor]:
        """
        인기도 기반 순위 매김

        Ranking Formula:
            score = (
                github_stars * 0.4 +
                recent_commits * 0.3 +
                doc_quality * 0.2 +
                community_size * 0.1
            )

        Normalization:
            - github_stars: log scale (0-1)
            - recent_commits: last 30 days (0-1)
            - doc_quality: README length + sections (0-1)
            - community_size: issues + discussions (0-1)
        """
        for competitor in competitors:
            score = 0
            score += self._normalize_stars(competitor.github_stars) * 0.4
            score += self._normalize_activity(competitor.recent_commits) * 0.3
            score += self._normalize_docs(competitor.readme_length) * 0.2
            score += self._normalize_community(competitor.community_size) * 0.1
            competitor.popularity_score = score

        return sorted(competitors, key=lambda x: x.popularity_score, reverse=True)
```

### 2. ProductAnalyzer

```python
class ProductAnalyzer:
    """경쟁사 제품 상세 분석"""

    def __init__(self, web_fetch_client):
        self.web_fetch = web_fetch_client
        self.strength_patterns = self._load_strength_patterns()
        self.weakness_indicators = self._load_weakness_indicators()

    def analyze_product(self, competitor: Competitor) -> ProductAnalysis:
        """
        제품 상세 분석

        Args:
            competitor: Competitor 객체 (URL, GitHub repo 포함)

        Returns:
            ProductAnalysis 객체 (특장점, 약점, 메트릭)

        Steps:
            1. README 분석 (핵심 기능)
            2. Documentation 분석 (완성도)
            3. Issues 분석 (사용자 불만)
            4. Reviews 분석 (실제 평가)

        Performance:
            - Target: <3분 per product
            - WebFetch 호출: 4-6회
            - 캐싱: 7일 TTL
        """
        analysis = ProductAnalysis(competitor.name)

        # 1. Fetch README
        readme = self._fetch_readme(competitor.github_url)
        analysis.strengths.extend(self._extract_strengths_from_readme(readme))

        # 2. Fetch Documentation
        docs = self._fetch_documentation(competitor.docs_url)
        analysis.doc_quality = self._assess_doc_quality(docs)

        # 3. Analyze Issues (top pain points)
        issues = self._fetch_issues(competitor.github_url, limit=50)
        analysis.weaknesses.extend(self._extract_weaknesses_from_issues(issues))

        # 4. Analyze Reviews (if available)
        if competitor.review_url:
            reviews = self._fetch_reviews(competitor.review_url)
            analysis.user_sentiment = self._analyze_sentiment(reviews)

        return analysis

    def _extract_strengths_from_readme(self, readme: str) -> List[Strength]:
        """
        README에서 특장점 추출

        Pattern Matching:
            - "Features:" 섹션 파싱
            - "Why [Product]?" 섹션 분석
            - Bullet points 추출
            - 강조 표현 탐지 ("powerful", "easy", "fast")

        Example:
            Input:
                ## Features
                - **Fast**: 10x faster than alternatives
                - **Easy**: One-line setup
                - **Powerful**: Advanced filtering

            Output:
                [
                    Strength("Fast", "10x faster than alternatives"),
                    Strength("Easy", "One-line setup"),
                    Strength("Powerful", "Advanced filtering")
                ]
        """
        strengths = []

        # Find "Features" section
        features_section = self._extract_section(readme, "Features")
        if features_section:
            bullet_points = self._parse_bullet_points(features_section)
            for point in bullet_points:
                strength = self._parse_strength(point)
                if strength:
                    strengths.append(strength)

        # Find "Why [Product]" section
        why_section = self._extract_section(readme, r"Why \w+\?")
        if why_section:
            reasons = self._parse_bullet_points(why_section)
            for reason in reasons:
                strength = self._parse_strength(reason)
                if strength:
                    strengths.append(strength)

        return strengths[:5]  # Top 5 strengths

    def _extract_weaknesses_from_issues(self, issues: List[Issue]) -> List[Weakness]:
        """
        GitHub Issues에서 약점 추출

        Strategy:
            1. 빈도 높은 문제 패턴 탐지
            2. "bug", "slow", "complicated" 키워드 필터링
            3. 해결 안 된 이슈 우선 순위

        Example:
            Input:
                [
                    Issue("App is slow with large datasets", open=True, comments=15),
                    Issue("UI is too complicated", open=True, comments=10),
                    Issue("Mobile version missing", open=True, comments=8)
                ]

            Output:
                [
                    Weakness("Performance", "Slow with large datasets", severity="high"),
                    Weakness("UX", "Complicated UI", severity="medium"),
                    Weakness("Platform", "No mobile version", severity="medium")
                ]
        """
        weaknesses = []
        issue_patterns = self._cluster_similar_issues(issues)

        for pattern, issue_group in issue_patterns.items():
            if len(issue_group) >= 3:  # At least 3 similar issues
                weakness = Weakness(
                    category=self._categorize_issue(pattern),
                    description=self._summarize_issues(issue_group),
                    severity=self._assess_severity(issue_group),
                    frequency=len(issue_group)
                )
                weaknesses.append(weakness)

        return sorted(weaknesses, key=lambda x: x.frequency, reverse=True)[:5]
```

### 3. DifferentiationGenerator

```python
class DifferentiationGenerator:
    """차별화 전략 생성"""

    def __init__(self):
        self.strategy_templates = self._load_strategy_templates()

    def generate_differentiation(
        self,
        competitors: List[ProductAnalysis],
        user_context: Optional[str] = None
    ) -> List[DifferentiationPoint]:
        """
        차별화 전략 생성

        Args:
            competitors: 경쟁사 분석 결과 리스트
            user_context: 사용자 컨텍스트 (선택)

        Returns:
            DifferentiationPoint 리스트 (최소 3개)

        Strategy:
            1. Gap Analysis (모든 경쟁사가 가지지 않은 기능)
            2. Weakness Exploitation (경쟁사 약점 공략)
            3. Combination Innovation (2개 이상 결합)
            4. Target Niche (특정 세그먼트 집중)

        Performance:
            - Target: <2분
            - AI 추론: 1-2회
        """
        differentiation_points = []

        # Strategy 1: Gap Analysis
        gaps = self._find_common_gaps(competitors)
        for gap in gaps[:2]:
            point = self._create_gap_based_differentiation(gap, competitors)
            differentiation_points.append(point)

        # Strategy 2: Weakness Exploitation
        common_weaknesses = self._find_common_weaknesses(competitors)
        if common_weaknesses:
            point = self._create_weakness_based_differentiation(
                common_weaknesses[0], competitors
            )
            differentiation_points.append(point)

        # Strategy 3: Combination Innovation (if needed)
        if len(differentiation_points) < 3:
            point = self._create_combination_differentiation(competitors)
            differentiation_points.append(point)

        # Strategy 4: Target Niche (bonus)
        if user_context:
            niche = self._identify_niche_opportunity(competitors, user_context)
            if niche:
                point = self._create_niche_differentiation(niche, competitors)
                differentiation_points.append(point)

        return differentiation_points[:3]  # Top 3

    def _find_common_gaps(self, competitors: List[ProductAnalysis]) -> List[str]:
        """
        모든 경쟁사가 가지지 않은 기능 탐지

        Example:
            Competitor 1: ["feature A", "feature B"]
            Competitor 2: ["feature A", "feature C"]
            Competitor 3: ["feature B", "feature C"]

            Common gaps: ["feature D", "feature E"] (아무도 없음)

        Implementation:
            - 모든 경쟁사 features 합집합
            - 업계 표준 features 리스트
            - 차집합 = gaps
        """
        all_features = set()
        for competitor in competitors:
            all_features.update(competitor.features)

        industry_standard_features = self._get_industry_features(
            competitors[0].category
        )

        gaps = industry_standard_features - all_features
        return list(gaps)

    def _create_gap_based_differentiation(
        self, gap: str, competitors: List[ProductAnalysis]
    ) -> DifferentiationPoint:
        """
        Gap 기반 차별화 포인트 생성

        Example:
            gap = "AI auto-priority"

            Output:
                DifferentiationPoint(
                    point="AI 자동 우선순위",
                    rationale="모든 경쟁사가 수동 우선순위만 제공",
                    target_market="시간 관리 어려운 바쁜 직장인",
                    implementation_complexity="medium",
                    estimated_impact="high"
                )
        """
        return DifferentiationPoint(
            point=gap,
            rationale=f"모든 경쟁사 ({len(competitors)}개)가 이 기능을 제공하지 않음",
            target_market=self._identify_target_for_gap(gap),
            implementation_complexity=self._assess_complexity(gap),
            estimated_impact=self._estimate_impact(gap, competitors)
        )
```

### 4. YAMLBuilder

```python
class YAMLBuilder:
    """YAML benchmarking 섹션 생성"""

    def build_yaml_section(
        self,
        competitors: List[ProductAnalysis],
        differentiation: List[DifferentiationPoint],
        target_market: Optional[dict] = None
    ) -> dict:
        """
        YAML benchmarking 섹션 생성

        Args:
            competitors: 경쟁사 분석 결과
            differentiation: 차별화 포인트
            target_market: 타겟 시장 정보

        Returns:
            YAML 딕셔너리 (P16 준수)

        Output Format:
            {
                "benchmarking": {
                    "competitors": [...],
                    "differentiation": [...],
                    "target_market": {...}
                }
            }
        """
        yaml_section = {
            "benchmarking": {
                "competitors": [],
                "differentiation": [],
                "target_market": target_market or {}
            }
        }

        # Add competitors
        for competitor in competitors:
            yaml_section["benchmarking"]["competitors"].append({
                "name": competitor.name,
                "github_stars": competitor.github_stars,
                "strengths": [s.to_dict() for s in competitor.strengths[:3]],
                "weaknesses": [w.to_dict() for w in competitor.weaknesses[:3]]
            })

        # Add differentiation
        for diff in differentiation:
            yaml_section["benchmarking"]["differentiation"].append({
                "point": diff.point,
                "rationale": diff.rationale,
                "target": diff.target_market,
                "complexity": diff.implementation_complexity,
                "impact": diff.estimated_impact
            })

        return yaml_section
```

---

## 📊 Data Models

### Competitor
```python
@dataclass
class Competitor:
    """경쟁사 제품 정보"""
    name: str
    github_url: Optional[str]
    docs_url: Optional[str]
    github_stars: int
    recent_commits: int
    readme_length: int
    community_size: int
    popularity_score: float = 0.0
```

### ProductAnalysis
```python
@dataclass
class ProductAnalysis:
    """제품 분석 결과"""
    name: str
    category: str
    strengths: List[Strength]
    weaknesses: List[Weakness]
    features: List[str]
    doc_quality: float  # 0-1 score
    user_sentiment: float  # -1 to 1
    github_stars: int
```

### Strength
```python
@dataclass
class Strength:
    """제품 특장점"""
    title: str
    description: str
    evidence: str  # Where found (README, docs, reviews)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description
        }
```

### Weakness
```python
@dataclass
class Weakness:
    """제품 약점"""
    category: str  # Performance, UX, Platform, etc.
    description: str
    severity: str  # low, medium, high
    frequency: int  # Number of related issues

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "description": self.description
        }
```

### DifferentiationPoint
```python
@dataclass
class DifferentiationPoint:
    """차별화 포인트"""
    point: str
    rationale: str
    target_market: str
    implementation_complexity: str  # low, medium, high
    estimated_impact: str  # low, medium, high
```

---

## ⚡ Performance Requirements

| Operation | Target | Max |
|-----------|--------|-----|
| search_competitors() | <5min | 10min |
| analyze_product() | <3min | 5min |
| generate_differentiation() | <2min | 5min |
| **Total Pipeline** | **<15min** | **30min** |

### Optimization Strategies

1. **Parallel Processing**
   ```python
   # Analyze competitors in parallel
   with ThreadPoolExecutor(max_workers=3) as executor:
       futures = [
           executor.submit(analyzer.analyze_product, comp)
           for comp in competitors
       ]
       results = [f.result() for f in futures]
   ```

2. **Caching**
   - Competitor search: 24시간 TTL
   - Product analysis: 7일 TTL
   - Cache key: hash(query + category)

3. **Rate Limiting**
   - WebSearch: 5 calls/min
   - WebFetch: 10 calls/min
   - Backoff strategy: exponential

---

## 🔒 Error Handling

### Graceful Degradation

```python
def search_competitors(self, query: str) -> List[Competitor]:
    try:
        results = self.web_search.search(query)
    except WebSearchTimeout:
        logger.warning("WebSearch timeout, using cached results")
        results = self.cache.get(query, [])
    except WebSearchQuotaExceeded:
        logger.error("WebSearch quota exceeded")
        return self._fallback_manual_list(query)

    if len(results) < 3:
        logger.warning(f"Only {len(results)} competitors found")
        # Still proceed with available data

    return results
```

### Retry Logic

```python
@retry(max_attempts=3, backoff=2.0)
def _fetch_readme(self, github_url: str) -> str:
    """Fetch README with retry logic"""
    response = self.web_fetch.fetch(f"{github_url}/README.md")
    if response.status_code != 200:
        raise FetchError(f"Failed to fetch README: {response.status_code}")
    return response.text
```

---

## 🧪 Testing Strategy

### Unit Tests (15+ tests)
- `test_search_competitors_returns_min_3()`
- `test_rank_by_popularity_descending()`
- `test_extract_strengths_from_readme()`
- `test_extract_weaknesses_from_issues()`
- `test_generate_differentiation_min_3()`
- `test_yaml_builder_p16_compliant()`

### Integration Tests (5+ tests)
- `test_full_pipeline_todo_app()`
- `test_full_pipeline_habit_tracker()`
- `test_error_handling_no_results()`
- `test_caching_works()`
- `test_performance_under_30min()`

### Performance Tests
- `test_search_under_5min()`
- `test_analysis_under_3min_per_product()`
- `test_total_pipeline_under_15min()`

---

## 🎯 Success Criteria

- [ ] 경쟁사 검색: 최소 3개, 목표 5개
- [ ] 분석 시간: <15분 (목표), <30분 (최대)
- [ ] 차별화 포인트: 최소 3개
- [ ] YAML 검증: P16 준수
- [ ] 테스트 커버리지: >90%
- [ ] 에러 처리: Graceful degradation

---

## 📝 Next Steps

1. **Phase 2: 구현**
   - `scripts/benchmark_analyzer.py` 작성
   - 4개 핵심 클래스 구현
   - WebSearch/WebFetch 통합

2. **Phase 3: TaskExecutor 통합**
   - P16 게이트 검증 추가
   - YAML 파싱 로직

3. **Phase 4: 테스트**
   - 20+ 테스트 작성
   - 실제 케이스 검증 (Todoist, Habitica)

---

**작성자**: Claude
**날짜**: 2025-11-04
**상태**: Design Complete
**다음 단계**: Phase 2 구현 시작
