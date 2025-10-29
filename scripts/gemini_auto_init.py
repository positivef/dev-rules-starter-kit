#!/usr/bin/env python3
"""
Gemini AI Auto-Initialization
Automatically runs when Gemini session starts
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


# Mark as Gemini environment
os.environ["GEMINI_AI"] = "1"

# Create .gemini directory if not exists
gemini_dir = Path(".gemini")
gemini_dir.mkdir(exist_ok=True)


class GeminiHandoffSession:
    """Gemini session with automatic handoff protocol"""

    def __init__(self, auto_init=True):
        """Initialize Gemini session"""
        self.agent_name = "Gemini"
        self.handoff_file = Path("HANDOFF_REPORT.md")
        self.context_hash = None
        self.instructions = None
        self.session_start = datetime.now()

        if auto_init:
            self._run_auto_init()

    def _run_auto_init(self):
        """Execute automatic initialization"""
        print("\n" + "🌟" * 30)
        print("  GEMINI AI - INTELLIGENT SESSION INITIALIZATION")
        print("🌟" * 30)

        # Import and run agent_auto_init
        sys.path.insert(0, "scripts")
        from agent_auto_init import gemini_init

        # Run initialization
        handoff_exists = gemini_init()

        # Parse handoff if exists
        if handoff_exists and self.handoff_file.exists():
            self._parse_handoff()

        # Show Gemini-specific features
        self._show_gemini_features()

    def _parse_handoff(self):
        """Parse handoff report for key information"""
        content = self.handoff_file.read_text(encoding="utf-8")

        # Extract instructions
        if "## 6. Instructions" in content:
            start = content.index("## 6. Instructions")
            end = content.index("##", start + 1) if "##" in content[start + 1 :] else len(content)
            self.instructions = content[start:end].strip()

        # Extract context hash
        for line in content.split("\n"):
            if "Context Hash:" in line:
                self.context_hash = line.split(":")[-1].strip()
                break

    def _show_gemini_features(self):
        """Display Gemini-specific features"""
        print("\n🚀 Gemini Enhanced Features:")
        print("  • AI-powered code analysis")
        print("  • Cross-verification with multiple sources")
        print("  • Intelligent handoff recommendations")
        print("  • Session persistence and recovery")

    def analyze_codebase(self):
        """Gemini's enhanced codebase analysis"""
        print("\n🔍 Running Gemini deep analysis...")

        # Run deep analyzer
        result = subprocess.run(["python", "scripts/deep_analyzer.py"], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Analysis complete")
            return result.stdout
        else:
            print("⚠️ Analysis failed")
            return None

    def create(self, summary: str, instructions: str, verify=True):
        """Create handoff with Gemini verification"""
        print("\n📝 Creating Gemini handoff report...")

        # Run tests if verify is True
        test_results = "Tests not run"
        if verify:
            print("Running verification tests...")
            test_result = subprocess.run(["pytest", "tests/", "-q"], capture_output=True, text=True)
            test_results = "All tests passed" if test_result.returncode == 0 else "Some tests failed"

        # Create handoff
        cmd = [
            "python",
            "scripts/create_handoff_report.py",
            "--author",
            self.agent_name,
            "--summary",
            summary,
            "--test-results",
            test_results,
            "--instructions",
            instructions,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Handoff created successfully")
            self._update_gemini_history(summary)
        else:
            print("❌ Handoff creation failed")

    def _update_gemini_history(self, summary):
        """Update Gemini session history"""
        history_file = gemini_dir / "session_history.json"

        history = []
        if history_file.exists():
            history = json.loads(history_file.read_text(encoding="utf-8"))

        history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "agent": self.agent_name,
                "summary": summary,
                "context_hash": self.context_hash,
            }
        )

        # Keep last 10 entries
        history = history[-10:]

        history_file.write_text(json.dumps(history, indent=2), encoding="utf-8")

    def verify_with_gemini_api(self, code_path: str):
        """Use Gemini API for code verification (if configured)"""
        # Check if verify_with_gemini.py exists
        verify_script = Path("scripts/verify_with_gemini.py")
        if not verify_script.exists():
            print("⚠️ Gemini API verification not configured")
            return None

        print("\n🤖 Verifying with Gemini API...")
        result = subprocess.run(["python", str(verify_script), code_path], capture_output=True, text=True)

        return result.stdout if result.returncode == 0 else None

    def view_report(self):
        """View current handoff report"""
        if self.handoff_file.exists():
            content = self.handoff_file.read_text(encoding="utf-8")
            print(content)
        else:
            print("No handoff report found")

    def update_status(self, status: str):
        """Update agent sync board"""
        subprocess.run(
            [
                "python",
                "scripts/multi_agent_sync.py",
                "update-status",
                self.agent_name,
                status,
                "--context-hash",
                self.context_hash or "unknown",
            ]
        )

    def get_session_info(self):
        """Get current session information"""
        duration = datetime.now() - self.session_start
        return {
            "agent": self.agent_name,
            "session_start": self.session_start.isoformat(),
            "duration": str(duration),
            "context_hash": self.context_hash,
            "has_instructions": bool(self.instructions),
        }


# Auto-create global session
gemini = GeminiHandoffSession()


# Export convenience functions
def create_handoff(summary, instructions, verify=True):
    """Quick handoff creation"""
    return gemini.create(summary, instructions, verify)


def analyze():
    """Run codebase analysis"""
    return gemini.analyze_codebase()


def verify_code(path):
    """Verify code with Gemini API"""
    return gemini.verify_with_gemini_api(path)


def view_report():
    """View handoff report"""
    return gemini.view_report()


def session_info():
    """Get session information"""
    return gemini.get_session_info()


# If running directly
if __name__ == "__main__":
    print("\n✅ Gemini session initialized!")
    print("\nAvailable functions:")
    print("  - create_handoff(summary, instructions)")
    print("  - analyze() - Deep codebase analysis")
    print("  - verify_code(path) - Gemini API verification")
    print("  - view_report() - View handoff report")
    print("  - session_info() - Current session details")

    if gemini.instructions:
        print("\n🎯 Current Task:")
        print(gemini.instructions[:200] + "..." if len(gemini.instructions) > 200 else gemini.instructions)
