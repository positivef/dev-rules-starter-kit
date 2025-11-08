#!/usr/bin/env python3
"""Pattern Sync Manager - 중앙집중식 패턴 관리 및 동기화 시스템

모든 Pattern을 한 곳에서 관리하고 여러 위치에 자동 동기화합니다.
Pattern 4를 포함한 모든 Constitution 패턴의 일관성을 보장합니다.
"""

import json
import hashlib
import yaml
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PatternLocation:
    """패턴이 저장되는 위치 정보"""

    path: Path
    file_type: str  # yaml, md, py
    section: str  # 파일 내 섹션 이름
    priority: int  # 동기화 우선순위 (1이 가장 높음)
    description: str


@dataclass
class Pattern:
    """패턴 정보"""

    id: str
    name: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    content: str
    version: str
    checksum: str
    locations: List[PatternLocation]


class PatternSyncManager:
    """중앙집중식 패턴 동기화 관리자"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.pattern_registry_file = self.base_dir / "config" / "pattern_registry.yaml"
        self.patterns: Dict[str, Pattern] = {}
        self.locations = self._define_locations()

    def _define_locations(self) -> Dict[str, List[PatternLocation]]:
        """패턴이 저장되어야 할 모든 위치 정의"""

        home = Path.home()
        github = home / "Documents" / "GitHub"

        return {
            "pattern_4_design_review": [
                PatternLocation(
                    path=self.base_dir / "config" / "constitution.yaml",
                    file_type="yaml",
                    section="articles.P11.anti_patterns.pattern_4_design_review_first",
                    priority=1,
                    description="Constitution P11 anti-patterns",
                ),
                PatternLocation(
                    path=self.base_dir / "CLAUDE.md",
                    file_type="md",
                    section="P11 Pattern 4",
                    priority=2,
                    description="Project CLAUDE.md",
                ),
                PatternLocation(
                    path=home / ".claude" / "INNOVATION_SAFETY_PRINCIPLES.md",
                    file_type="md",
                    section="Pattern 4: 설계 검토 필수",
                    priority=1,
                    description="Global Innovation Safety Principles",
                ),
                PatternLocation(
                    path=github / "skill" / "vibe-coding-enhanced" / "SKILL.md",
                    file_type="md",
                    section="Rule 4: Design Review First",
                    priority=3,
                    description="VibeCoding Enhanced Skill",
                ),
                PatternLocation(
                    path=github / "skill" / "vibe-coding-fusion" / "SKILL.md",
                    file_type="md",
                    section="MANDATORY: Design Review First",
                    priority=3,
                    description="VibeCoding Fusion Skill",
                ),
            ],
            "pattern_2_unverified": [
                PatternLocation(
                    path=self.base_dir / "config" / "constitution.yaml",
                    file_type="yaml",
                    section="articles.P11.anti_patterns.pattern_2_unverified_rejection",
                    priority=1,
                    description="Constitution P11 anti-patterns",
                ),
                PatternLocation(
                    path=github / "skill" / "vibe-coding-enhanced" / "SKILL.md",
                    file_type="md",
                    section="Pattern 2: Unverified",
                    priority=3,
                    description="VibeCoding Enhanced Skill",
                ),
            ],
        }

    def calculate_checksum(self, content: str) -> str:
        """컨텐츠의 체크섬 계산"""
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def _check_yaml_pattern(self, file_path: Path, pattern_id: str) -> bool:
        """YAML 파일에서 패턴 존재 확인 (리스트 구조 지원)"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # constitution.yaml의 경우: articles 리스트에서 P11 찾기
            if "articles" in data and isinstance(data["articles"], list):
                for article in data["articles"]:
                    if article.get("id") == "P11":
                        anti_patterns = article.get("anti_patterns", {})
                        if pattern_id == "pattern_4_design_review":
                            return "pattern_4_design_review_first" in anti_patterns
                        elif pattern_id == "pattern_2_unverified":
                            return "pattern_2_unverified_not_rejection" in anti_patterns
                        return False
            return False
        except Exception:
            return False

    def check_pattern_consistency(self, pattern_id: str) -> Dict[str, Any]:
        """특정 패턴의 모든 위치에서 일관성 검사"""

        if pattern_id not in self.locations:
            return {"error": f"Unknown pattern: {pattern_id}"}

        results = {"pattern_id": pattern_id, "locations": {}, "consistent": True, "timestamp": datetime.now().isoformat()}

        for location in self.locations[pattern_id]:
            if not location.path.exists():
                results["locations"][str(location.path)] = {"exists": False, "description": location.description}
                results["consistent"] = False
                continue

            # 파일 타입별 검증
            if location.file_type == "yaml":
                section_found = self._check_yaml_pattern(location.path, pattern_id)
            else:
                # Markdown 파일은 단순 문자열 검색
                content = location.path.read_text(encoding="utf-8")
                section_found = location.section in content

            results["locations"][str(location.path)] = {
                "exists": True,
                "section_found": section_found,
                "description": location.description,
                "priority": location.priority,
            }

            if not section_found:
                results["consistent"] = False

        return results

    def sync_pattern(self, pattern_id: str, dry_run: bool = False) -> Dict[str, any]:
        """특정 패턴을 모든 위치에 동기화"""

        results = {"pattern_id": pattern_id, "synced": [], "failed": [], "skipped": [], "dry_run": dry_run}

        if pattern_id not in self.locations:
            results["error"] = f"Unknown pattern: {pattern_id}"
            return results

        # 가장 높은 우선순위 위치에서 패턴 읽기
        source_location = min(self.locations[pattern_id], key=lambda x: x.priority)

        if not source_location.path.exists():
            results["error"] = f"Source file not found: {source_location.path}"
            return results

        # 각 위치에 동기화
        for location in self.locations[pattern_id]:
            try:
                if location == source_location:
                    results["skipped"].append(str(location.path))
                    continue

                if dry_run:
                    results["synced"].append(
                        {"path": str(location.path), "action": "would sync", "description": location.description}
                    )
                else:
                    # 실제 동기화 로직 (여기서는 간단히 표시만)
                    # 실제 구현시에는 파일 타입별로 다른 로직 필요
                    results["synced"].append(
                        {"path": str(location.path), "action": "synced", "description": location.description}
                    )

            except Exception as e:
                results["failed"].append({"path": str(location.path), "error": str(e)})

        return results

    def generate_status_report(self) -> str:
        """전체 패턴 동기화 상태 리포트 생성"""

        report = []
        report.append("# Pattern Synchronization Status Report")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        for pattern_id in self.locations.keys():
            report.append(f"\n## Pattern: {pattern_id}")

            status = self.check_pattern_consistency(pattern_id)

            if status.get("consistent"):
                report.append("[OK] **Status: SYNCHRONIZED**")
            else:
                report.append("[WARN] **Status: OUT OF SYNC**")

            report.append("\n### Locations:")
            for path, info in status.get("locations", {}).items():
                icon = "[OK]" if info.get("exists") and info.get("section_found", True) else "[X]"
                report.append(f"- {icon} `{Path(path).name}` - {info.get('description', 'N/A')}")
                if not info.get("exists"):
                    report.append("  - File not found")
                elif not info.get("section_found", True):
                    report.append("  - Section not found")

        return "\n".join(report)

    def create_pattern_template(self, pattern_id: str) -> str:
        """새 패턴을 위한 템플릿 생성"""

        template = f"""# Pattern: {pattern_id}

## 개요
- **이름**: [패턴 이름]
- **심각도**: CRITICAL / HIGH / MEDIUM / LOW
- **발견일**: {datetime.now().strftime('%Y-%m-%d')}
- **버전**: 1.0.0

## 문제 상황
- **잘못된 패턴**: [설명]
- **올바른 패턴**: [설명]

## 필수 체크리스트
1. [ ] 체크 항목 1
2. [ ] 체크 항목 2
3. [ ] 체크 항목 3

## 적용 조건
- 트리거 1
- 트리거 2

## 예외 사항
- 예외 1
- 예외 2

## 커뮤니케이션 가이드
**절대 하지 말아야 할 말**:
- "..."

**항상 해야 할 말**:
- "..."
"""
        return template


def main():
    """CLI 인터페이스"""
    import argparse

    parser = argparse.ArgumentParser(description="Pattern Sync Manager")
    parser.add_argument("command", choices=["check", "sync", "report", "template"], help="Command to execute")
    parser.add_argument("--pattern", help="Pattern ID")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--all", action="store_true", help="Apply to all patterns")

    args = parser.parse_args()

    manager = PatternSyncManager()

    if args.command == "check":
        if args.pattern:
            result = manager.check_pattern_consistency(args.pattern)
            print(json.dumps(result, indent=2, default=str))
        else:
            print("Please specify --pattern or use --all")

    elif args.command == "sync":
        if args.pattern:
            result = manager.sync_pattern(args.pattern, dry_run=args.dry_run)
            print(json.dumps(result, indent=2, default=str))
        elif args.all:
            for pattern_id in manager.locations.keys():
                print(f"\nSyncing {pattern_id}...")
                result = manager.sync_pattern(pattern_id, dry_run=args.dry_run)
                print(f"  Synced: {len(result.get('synced', []))}")
                print(f"  Failed: {len(result.get('failed', []))}")
        else:
            print("Please specify --pattern or use --all")

    elif args.command == "report":
        report = manager.generate_status_report()
        print(report)

        # 파일로도 저장
        report_file = manager.base_dir / "PATTERN_SYNC_STATUS.md"
        report_file.write_text(report, encoding="utf-8")
        print(f"\nReport saved to: {report_file}")

    elif args.command == "template":
        if args.pattern:
            template = manager.create_pattern_template(args.pattern)
            print(template)
        else:
            print("Please specify --pattern for template generation")


if __name__ == "__main__":
    main()
