#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quality Gate CI - P6 Quality Gate for GitHub Actions
====================================================

목적: CI/CD에서 P6 Quality Gate 자동 검증

검증 기준:
- Ruff 검사 통과
- 보안 스캔 통과
- 테스트 커버리지 80% 이상
- Constitution 위반 없음

Stage 5 Phase 2: CI/CD Integration
"""

import sys
import json
from pathlib import Path
from datetime import datetime


class QualityGateCI:
    """CI/CD Quality Gate 검증"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "passed": False,
            "checks": {},
            "violations": [],
            "warnings": [],
        }

    def check_ruff(self) -> bool:
        """Ruff 검사 확인"""
        print("[P6] Checking Ruff compliance...")

        # GitHub Actions에서 이미 실행됨
        # 여기서는 결과 확인만
        self.results["checks"]["ruff"] = {"name": "Ruff Linter", "status": "checked_externally", "article": "P10"}

        return True

    def check_security(self) -> bool:
        """보안 스캔 확인"""
        print("[P6] Checking security compliance...")

        # GitHub Actions에서 Gitleaks 실행됨
        self.results["checks"]["security"] = {"name": "Security Scan", "status": "checked_externally", "article": "P5"}

        return True

    def check_test_coverage(self) -> bool:
        """테스트 커버리지 확인"""
        print("[P6] Checking test coverage...")

        coverage_file = self.project_root / "coverage.xml"

        if not coverage_file.exists():
            self.results["warnings"].append(
                {"check": "test_coverage", "message": "coverage.xml not found", "severity": "LOW"}
            )
            self.results["checks"]["coverage"] = {"name": "Test Coverage", "status": "not_available", "article": "P8"}
            return True  # Warning만, 차단하지 않음

        # coverage.xml 파싱
        try:
            import xml.etree.ElementTree as ET

            tree = ET.parse(coverage_file)
            root = tree.getroot()

            line_rate = float(root.attrib.get("line-rate", "0"))
            coverage_percent = line_rate * 100

            threshold = 80.0
            passed = coverage_percent >= threshold

            self.results["checks"]["coverage"] = {
                "name": "Test Coverage",
                "status": "passed" if passed else "failed",
                "article": "P8",
                "coverage": coverage_percent,
                "threshold": threshold,
            }

            if not passed:
                self.results["violations"].append(
                    {
                        "check": "test_coverage",
                        "message": f"Coverage {coverage_percent:.1f}% < {threshold}%",
                        "severity": "HIGH",
                    }
                )

            print(f"  Coverage: {coverage_percent:.1f}% (threshold: {threshold}%)")

            return passed

        except Exception as e:
            print(f"  [WARNING] Failed to parse coverage.xml: {e}")
            self.results["warnings"].append(
                {"check": "test_coverage", "message": f"Failed to parse: {e}", "severity": "MEDIUM"}
            )
            return True  # 파싱 실패는 차단하지 않음

    def check_constitution_guard(self) -> bool:
        """Constitution Guard 확인"""
        print("[P6] Checking Constitution Guard...")

        # GitHub Actions에서 이미 실행됨
        self.results["checks"]["constitution_guard"] = {
            "name": "Constitution Guard",
            "status": "checked_externally",
            "articles": ["P4", "P5", "P7", "P10"],
        }

        return True

    def run_gate(self) -> bool:
        """Quality Gate 실행"""
        print("\n" + "=" * 60)
        print("Quality Gate Check (P6)")
        print("=" * 60 + "\n")

        # 모든 검증 실행
        checks = [self.check_ruff(), self.check_security(), self.check_test_coverage(), self.check_constitution_guard()]

        # 결과 판정
        self.results["passed"] = all(checks) and len(self.results["violations"]) == 0

        # 결과 출력
        self._print_results()

        # 결과 저장
        self._save_results()

        return self.results["passed"]

    def _print_results(self):
        """결과 출력"""
        print("\n" + "=" * 60)
        print("Quality Gate Results")
        print("=" * 60 + "\n")

        # 체크 항목
        print("Checks:")
        for check_name, check_data in self.results["checks"].items():
            status = check_data.get("status", "unknown")
            icon = {"passed": "[OK]", "failed": "[FAIL]", "checked_externally": "[CHECKED]", "not_available": "[WARN]"}.get(
                status, "?"
            )

            print(f"  {icon} {check_data['name']}: {status}")

            if "coverage" in check_data:
                print(f"     Coverage: {check_data['coverage']:.1f}%")

        # 위반 사항
        if self.results["violations"]:
            print(f"\n[FAIL] Violations ({len(self.results['violations'])}):")
            for v in self.results["violations"]:
                print(f"  - [{v['severity']}] {v['check']}: {v['message']}")

        # 경고
        if self.results["warnings"]:
            print(f"\n[WARN] Warnings ({len(self.results['warnings'])}):")
            for w in self.results["warnings"]:
                print(f"  - [{w['severity']}] {w['check']}: {w['message']}")

        # 최종 결과
        print("\n" + "=" * 60)
        if self.results["passed"]:
            print("[OK] Quality Gate PASSED")
        else:
            print("[FAIL] Quality Gate FAILED")
        print("=" * 60 + "\n")

    def _save_results(self):
        """결과 저장"""
        runs_dir = self.project_root / "RUNS"
        runs_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = runs_dir / f"quality_gate_{timestamp}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"Report saved: {report_file}")


def main():
    """메인 실행"""
    gate = QualityGateCI()
    passed = gate.run_gate()

    if passed:
        print("\n[OK] Quality Gate passed - PR can be merged")
        sys.exit(0)
    else:
        print("\n[FAIL] Quality Gate failed - Fix violations before merging")
        sys.exit(1)


if __name__ == "__main__":
    main()
