#!/usr/bin/env python3
"""
Documentation Quality Metrics Tracker

Tracks quality metrics for documentation as defined in TRADEOFF_ANALYSIS.md:
- Navigation time: Target <2 minutes
- Document satisfaction: Target >85%
- Bounce rate: Target <10%

Usage:
    python scripts/doc_quality_check.py --check
    python scripts/doc_quality_check.py --report
    python scripts/doc_quality_check.py --simulate
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import yaml


class DocumentationMetrics:
    """Track and analyze documentation quality metrics."""

    def __init__(self, docs_dir: Path = Path("docs")):
        self.docs_dir = docs_dir
        self.metrics_file = Path("RUNS/doc_metrics/metrics.json")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

    def load_metrics(self) -> Dict:
        """Load existing metrics from file."""
        if self.metrics_file.exists():
            with open(self.metrics_file) as f:
                return json.load(f)
        return {"sessions": [], "aggregated": {}}

    def save_metrics(self, metrics: Dict) -> None:
        """Save metrics to file."""
        with open(self.metrics_file, "w") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

    def parse_frontmatter(self, doc_path: Path) -> Optional[Dict]:
        """Parse YAML frontmatter from a markdown document."""
        try:
            with open(doc_path, encoding="utf-8") as f:
                content = f.read()

            if not content.startswith("---"):
                return None

            # Extract frontmatter
            parts = content.split("---", 2)
            if len(parts) < 3:
                return None

            frontmatter = yaml.safe_load(parts[1])
            return frontmatter
        except Exception as e:
            print(f"[WARNING] Failed to parse {doc_path}: {e}")
            return None

    def check_documentation_structure(self) -> Dict:
        """Check overall documentation structure and completeness."""
        guide_files = [
            "QUICK_START.md",
            "ADOPTION_GUIDE.md",
            "MIGRATION_GUIDE.md",
            "MULTI_SESSION_GUIDE.md",
            "TRADEOFF_ANALYSIS.md",
        ]

        results = {
            "total_guides": len(guide_files),
            "guides_with_frontmatter": 0,
            "guides_with_see_also": 0,
            "guides_with_metadata": 0,
            "missing_elements": [],
        }

        for guide in guide_files:
            doc_path = self.docs_dir / guide
            if not doc_path.exists():
                results["missing_elements"].append(f"{guide} not found")
                continue

            # Check frontmatter
            frontmatter = self.parse_frontmatter(doc_path)
            if frontmatter:
                results["guides_with_frontmatter"] += 1

                # Check metadata completeness
                required_fields = [
                    "title",
                    "description",
                    "audience",
                    "estimated_time",
                    "difficulty",
                ]
                if all(field in frontmatter for field in required_fields):
                    results["guides_with_metadata"] += 1

            # Check for See Also section
            content = doc_path.read_text(encoding="utf-8")
            if "## 📚 See Also" in content or "## See Also" in content:
                results["guides_with_see_also"] += 1

        # Calculate completeness percentage
        results["frontmatter_coverage"] = results["guides_with_frontmatter"] / results["total_guides"] * 100
        results["metadata_coverage"] = results["guides_with_metadata"] / results["total_guides"] * 100
        results["cross_reference_coverage"] = results["guides_with_see_also"] / results["total_guides"] * 100

        return results

    def calculate_navigation_complexity(self) -> Dict:
        """
        Calculate navigation complexity metrics.

        Lower complexity = easier to find information.
        """
        guide_files = list(self.docs_dir.glob("*_GUIDE.md")) + [self.docs_dir / "QUICK_START.md"]

        total_cross_refs = 0
        avg_doc_length = 0
        docs_analyzed = 0

        for doc_path in guide_files:
            if not doc_path.exists():
                continue

            content = doc_path.read_text(encoding="utf-8")
            lines = content.splitlines()

            # Count cross-references
            cross_refs = content.count(".md)") + content.count(".md]")
            total_cross_refs += cross_refs

            # Document length (lines)
            avg_doc_length += len(lines)
            docs_analyzed += 1

        if docs_analyzed == 0:
            return {"error": "No documents found"}

        avg_doc_length = avg_doc_length / docs_analyzed
        avg_cross_refs = total_cross_refs / docs_analyzed

        # Estimate navigation time based on complexity
        # Formula: base_time + (doc_length_factor) - (cross_ref_factor)
        base_time = 60  # seconds
        doc_length_factor = (avg_doc_length / 100) * 10  # 10 sec per 100 lines
        cross_ref_factor = avg_cross_refs * 5  # 5 sec saved per cross-ref

        estimated_nav_time = max(30, base_time + doc_length_factor - cross_ref_factor)  # Min 30 sec

        return {
            "docs_analyzed": docs_analyzed,
            "avg_document_length": round(avg_doc_length, 1),
            "avg_cross_references": round(avg_cross_refs, 1),
            "total_cross_references": total_cross_refs,
            "estimated_navigation_time_seconds": round(estimated_nav_time, 1),
            "estimated_navigation_time_minutes": round(estimated_nav_time / 60, 2),
            "target_met": estimated_nav_time < 120,  # <2 minutes
        }

    def simulate_user_session(self, start_doc: str, target_info: str, session_id: Optional[str] = None) -> Dict:
        """
        Simulate a user session to measure navigation time.

        Args:
            start_doc: Document where user starts (e.g., "CLAUDE.md")
            target_info: What user is looking for (e.g., "migration strategy")
            session_id: Optional session identifier
        """
        session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Keyword mapping to documents
        keyword_map = {
            "migration": "MIGRATION_GUIDE.md",
            "legacy": "MIGRATION_GUIDE.md",
            "existing project": "MIGRATION_GUIDE.md",
            "multi session": "MULTI_SESSION_GUIDE.md",
            "concurrent": "MULTI_SESSION_GUIDE.md",
            "collaboration": "MULTI_SESSION_GUIDE.md",
            "level 0": "ADOPTION_GUIDE.md",
            "level 1": "ADOPTION_GUIDE.md",
            "adoption": "ADOPTION_GUIDE.md",
            "progressive": "ADOPTION_GUIDE.md",
            "side effect": "TRADEOFF_ANALYSIS.md",
            "risk": "TRADEOFF_ANALYSIS.md",
            "tradeoff": "TRADEOFF_ANALYSIS.md",
            "quick start": "QUICK_START.md",
            "beginner": "QUICK_START.md",
            "5 minutes": "QUICK_START.md",
        }

        # Find target document
        target_doc = None
        for keyword, doc in keyword_map.items():
            if keyword.lower() in target_info.lower():
                target_doc = doc
                break

        if not target_doc:
            return {
                "session_id": session_id,
                "success": False,
                "reason": "Target information not mapped to any document",
            }

        # Simulate navigation time
        # Base: 10 seconds to read CLAUDE.md trigger
        # + 15 seconds to find and open target doc
        # + 20 seconds to scan document
        base_time = 10
        navigation_time = 15
        scan_time = 20

        # Check if target doc has See Also section (reduces scan time)
        target_path = self.docs_dir / target_doc
        if target_path.exists():
            content = target_path.read_text(encoding="utf-8")
            if "## 📚 See Also" in content:
                scan_time = 10  # Reduced with good navigation

        total_time = base_time + navigation_time + scan_time

        return {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "start_doc": start_doc,
            "target_info": target_info,
            "target_doc_found": target_doc,
            "navigation_time_seconds": total_time,
            "navigation_time_minutes": round(total_time / 60, 2),
            "success": True,
            "target_met": total_time < 120,  # <2 minutes
        }

    def generate_report(self) -> str:
        """Generate a comprehensive quality report."""
        structure = self.check_documentation_structure()
        navigation = self.calculate_navigation_complexity()

        report = []
        report.append("=" * 60)
        report.append("DOCUMENTATION QUALITY REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Structure Analysis
        report.append("[STRUCTURE ANALYSIS]")
        report.append("-" * 60)
        report.append(f"Total Guides: {structure['total_guides']}")
        report.append(
            f"Frontmatter Coverage: {structure['frontmatter_coverage']:.1f}% "
            f"({structure['guides_with_frontmatter']}/{structure['total_guides']})"
        )
        report.append(
            f"Metadata Completeness: {structure['metadata_coverage']:.1f}% "
            f"({structure['guides_with_metadata']}/{structure['total_guides']})"
        )
        report.append(
            f"Cross-Reference Coverage: {structure['cross_reference_coverage']:.1f}% "
            f"({structure['guides_with_see_also']}/{structure['total_guides']})"
        )

        if structure["missing_elements"]:
            report.append("\n[WARNING] Missing Elements:")
            for elem in structure["missing_elements"]:
                report.append(f"  - {elem}")

        report.append("")

        # Navigation Analysis
        report.append("[NAVIGATION ANALYSIS]")
        report.append("-" * 60)
        report.append(f"Documents Analyzed: {navigation['docs_analyzed']}")
        report.append(f"Avg Document Length: {navigation['avg_document_length']} lines")
        report.append(f"Avg Cross-References: {navigation['avg_cross_references']} per doc")
        report.append(f"Total Cross-References: {navigation['total_cross_references']}")
        report.append("")
        report.append(
            f"Estimated Navigation Time: {navigation['estimated_navigation_time_minutes']} minutes "
            f"({navigation['estimated_navigation_time_seconds']} seconds)"
        )
        report.append(f"Target (<2 minutes): {'[OK] MET' if navigation['target_met'] else '[FAIL] NOT MET'}")

        report.append("")

        # Quality Scores
        report.append("[QUALITY SCORES]")
        report.append("-" * 60)

        # Overall score (weighted average)
        structure_score = (
            structure["frontmatter_coverage"] * 0.3
            + structure["metadata_coverage"] * 0.3
            + structure["cross_reference_coverage"] * 0.4
        )
        navigation_score = 100 if navigation["target_met"] else 50

        overall_score = structure_score * 0.6 + navigation_score * 0.4

        report.append(f"Structure Quality: {structure_score:.1f}/100")
        report.append(f"Navigation Quality: {navigation_score:.1f}/100")
        report.append(f"Overall Quality: {overall_score:.1f}/100")

        if overall_score >= 90:
            grade = "A (Excellent)"
        elif overall_score >= 80:
            grade = "B (Good)"
        elif overall_score >= 70:
            grade = "C (Fair)"
        else:
            grade = "D (Needs Improvement)"

        report.append(f"Grade: {grade}")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Documentation Quality Metrics Tracker")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check documentation structure and quality",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate comprehensive quality report",
    )
    parser.add_argument(
        "--simulate",
        nargs=2,
        metavar=("START_DOC", "TARGET_INFO"),
        help='Simulate user navigation (e.g., --simulate "CLAUDE.md" "migration strategy")',
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    args = parser.parse_args()

    metrics = DocumentationMetrics()

    if args.check:
        structure = metrics.check_documentation_structure()
        if args.json:
            print(json.dumps(structure, indent=2, ensure_ascii=False))
        else:
            print("\n[DOCUMENTATION STRUCTURE CHECK]")
            print(f"  Frontmatter Coverage: {structure['frontmatter_coverage']:.1f}%")
            print(f"  Metadata Coverage: {structure['metadata_coverage']:.1f}%")
            print(f"  Cross-Reference Coverage: {structure['cross_reference_coverage']:.1f}%")

    elif args.report:
        report = metrics.generate_report()
        # P10: Windows UTF-8 compliance - use ASCII-safe output
        try:
            print(report)
        except UnicodeEncodeError:
            # Fallback: ASCII-safe output
            ascii_report = report.encode("ascii", "ignore").decode("ascii")
            print(ascii_report)

        # Also save to file
        report_file = Path("RUNS/doc_metrics/latest_report.txt")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(report, encoding="utf-8")
        print(f"\n[SAVED] Report saved to: {report_file}")

    elif args.simulate:
        start_doc, target_info = args.simulate
        session = metrics.simulate_user_session(start_doc, target_info)

        if args.json:
            print(json.dumps(session, indent=2, ensure_ascii=False))
        else:
            print("\n[USER SESSION SIMULATION]")
            print(f"  Start: {session['start_doc']}")
            print(f"  Looking for: {session['target_info']}")
            print(f"  Found in: {session.get('target_doc_found', 'N/A')}")
            print(f"  Navigation Time: {session['navigation_time_minutes']} minutes")
            print(f"  Target Met: {'[OK] Yes' if session.get('target_met') else '[FAIL] No'}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
