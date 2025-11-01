#!/usr/bin/env python3
"""
Session Report Scheduler - 자동 리포트 생성 및 전송 스케줄러

Features:
- 주간/월간 자동 리포트 생성
- 이메일 전송 (선택적)
- 슬랙 알림 (선택적)
- Windows Task Scheduler / cron 통합

Usage:
    # 단일 실행
    python scripts/session_report_scheduler.py --run-once

    # 백그라운드 스케줄러 (계속 실행)
    python scripts/session_report_scheduler.py --schedule weekly

    # Windows Task Scheduler 설정
    python scripts/session_report_scheduler.py --setup-windows-task
"""

import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import subprocess
import platform

sys.path.insert(0, str(Path(__file__).parent))

from session_report_generator import SessionReportGenerator
from notification_utils import send_slack_notification

# 선택적 import
try:
    import schedule

    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("[INFO] schedule library not available. Background scheduling disabled.")

# 선택적 import
try:
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    print("[INFO] email libraries not available. Email sending disabled.")


class SessionReportScheduler:
    """세션 리포트 스케줄러"""

    def __init__(self, config_file: str = "config/report_scheduler.json"):
        """
        초기화

        Args:
            config_file: 설정 파일 경로
        """
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.generator = SessionReportGenerator()
        self.last_run_file = Path("RUNS/reports/last_run.json")

    def load_config(self) -> Dict[str, Any]:
        """설정 로드"""
        default_config = {
            "enabled": True,
            "schedules": {
                "daily": {"enabled": False, "time": "09:00", "format": "html", "send_email": False, "send_slack": False},
                "weekly": {
                    "enabled": True,
                    "day": "monday",
                    "time": "09:00",
                    "format": "html",
                    "send_email": False,
                    "send_slack": True,
                },
                "monthly": {
                    "enabled": False,
                    "day": 1,
                    "time": "09:00",
                    "format": "pdf",
                    "send_email": True,
                    "send_slack": True,
                },
            },
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "from_email": "",
                "from_password": "",
                "to_emails": [],
                "use_tls": True,
            },
            "slack": {"enabled": False, "webhook_url": ""},
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # 기본 설정과 병합
                    return self._merge_configs(default_config, loaded_config)
            except Exception as e:
                print(f"[WARN] Failed to load config: {e}")

        # 기본 설정 저장
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """설정 병합 (재귀적)"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def generate_daily_report(self) -> Optional[str]:
        """일일 리포트 생성"""
        print(f"[SCHEDULER] Generating daily report at {datetime.now()}")

        config = self.config["schedules"]["daily"]
        report_file = self.generator.generate_report(period="daily", days=1, format=config.get("format", "html"))

        if report_file:
            self._handle_report_delivery(report_file, "daily", config)

        return report_file

    def generate_weekly_report(self) -> Optional[str]:
        """주간 리포트 생성"""
        print(f"[SCHEDULER] Generating weekly report at {datetime.now()}")

        config = self.config["schedules"]["weekly"]
        report_file = self.generator.generate_report(period="weekly", days=7, format=config.get("format", "html"))

        if report_file:
            self._handle_report_delivery(report_file, "weekly", config)

        return report_file

    def generate_monthly_report(self) -> Optional[str]:
        """월간 리포트 생성"""
        print(f"[SCHEDULER] Generating monthly report at {datetime.now()}")

        config = self.config["schedules"]["monthly"]
        report_file = self.generator.generate_report(period="monthly", days=30, format=config.get("format", "html"))

        if report_file:
            self._handle_report_delivery(report_file, "monthly", config)

        return report_file

    def _handle_report_delivery(self, report_file: str, period: str, config: Dict[str, Any]) -> None:
        """리포트 전달 처리"""

        # 이메일 전송
        if config.get("send_email") and self.config["email"].get("enabled"):
            self.send_email_report(report_file, period)

        # Slack 알림
        if config.get("send_slack") and self.config["slack"].get("enabled"):
            self.send_slack_notification(report_file, period)

        # 마지막 실행 기록
        self.save_last_run(period, report_file)

    def send_email_report(self, report_file: str, period: str) -> bool:
        """이메일로 리포트 전송"""
        if not EMAIL_AVAILABLE:
            print("[WARN] Email libraries not available")
            return False

        email_config = self.config["email"]

        if not email_config.get("from_email") or not email_config.get("to_emails"):
            print("[WARN] Email configuration incomplete")
            return False

        try:
            # 이메일 구성
            msg = MIMEMultipart()
            msg["From"] = email_config["from_email"]
            msg["To"] = ", ".join(email_config["to_emails"])
            msg["Subject"] = f'Session Report - {period.title()} ({datetime.now().strftime("%Y-%m-%d")})'

            # 본문
            body = f"""
            Session Management {period.title()} Report

            Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            Report File: {Path(report_file).name}

            Please find the attached report for your review.

            Best regards,
            SessionManager Automation
            """

            msg.attach(MIMEText(body, "plain"))

            # 첨부 파일
            with open(report_file, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={Path(report_file).name}")
                msg.attach(part)

            # SMTP 연결 및 전송
            with smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"]) as server:
                if email_config.get("use_tls"):
                    server.starttls()
                server.login(email_config["from_email"], email_config["from_password"])
                server.send_message(msg)

            print(f"[SUCCESS] Email sent to {email_config['to_emails']}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to send email: {e}")
            return False

    def send_slack_notification(self, report_file: str, period: str) -> bool:
        """Slack으로 알림 전송"""
        slack_config = self.config["slack"]

        if not slack_config.get("webhook_url"):
            print("[WARN] Slack webhook URL not configured")
            return False

        # 간단한 분석 결과 로드
        analysis_file = Path(report_file).with_suffix(".json")
        summary = "Report generated successfully"

        if analysis_file.exists():
            try:
                with open(analysis_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    stats = data.get("analysis", {}).get("execution_stats", {})
                    summary = f"Tasks: {stats.get('total_tasks', 0)}, " f"Success Rate: {stats.get('success_rate', 0):.1f}%"
            except Exception:
                pass

        message = f"""
*Session Report - {period.title()}*
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
{summary}
Report: {Path(report_file).name}
        """

        return send_slack_notification(message, slack_config["webhook_url"])

    def save_last_run(self, period: str, report_file: str) -> None:
        """마지막 실행 정보 저장"""
        last_run_data = {}

        if self.last_run_file.exists():
            try:
                with open(self.last_run_file, "r", encoding="utf-8") as f:
                    last_run_data = json.load(f)
            except Exception:
                pass

        last_run_data[period] = {"timestamp": datetime.now().isoformat(), "report_file": report_file}

        self.last_run_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.last_run_file, "w", encoding="utf-8") as f:
            json.dump(last_run_data, f, indent=2)

    def setup_schedule(self) -> None:
        """스케줄 설정"""
        if not SCHEDULE_AVAILABLE:
            print("[ERROR] schedule library is required for scheduling")
            print("Install with: pip install schedule")
            return

        schedules = self.config["schedules"]

        # Daily
        if schedules["daily"]["enabled"]:
            schedule.every().day.at(schedules["daily"]["time"]).do(self.generate_daily_report)
            print(f"[SCHEDULE] Daily report scheduled at {schedules['daily']['time']}")

        # Weekly
        if schedules["weekly"]["enabled"]:
            day = schedules["weekly"]["day"].lower()
            time = schedules["weekly"]["time"]

            if day == "monday":
                schedule.every().monday.at(time).do(self.generate_weekly_report)
            elif day == "tuesday":
                schedule.every().tuesday.at(time).do(self.generate_weekly_report)
            elif day == "wednesday":
                schedule.every().wednesday.at(time).do(self.generate_weekly_report)
            elif day == "thursday":
                schedule.every().thursday.at(time).do(self.generate_weekly_report)
            elif day == "friday":
                schedule.every().friday.at(time).do(self.generate_weekly_report)
            elif day == "saturday":
                schedule.every().saturday.at(time).do(self.generate_weekly_report)
            elif day == "sunday":
                schedule.every().sunday.at(time).do(self.generate_weekly_report)

            print(f"[SCHEDULE] Weekly report scheduled on {day} at {time}")

        # Monthly
        if schedules["monthly"]["enabled"]:
            # Note: schedule library doesn't have built-in monthly support
            # We'll check daily and run on the specified day
            def check_monthly():
                if datetime.now().day == schedules["monthly"]["day"]:
                    self.generate_monthly_report()

            schedule.every().day.at(schedules["monthly"]["time"]).do(check_monthly)
            print(
                f"[SCHEDULE] Monthly report scheduled on day {schedules['monthly']['day']} at {schedules['monthly']['time']}"
            )

    def run_scheduler(self) -> None:
        """스케줄러 실행 (무한 루프)"""
        if not SCHEDULE_AVAILABLE:
            print("[ERROR] schedule library is required for background scheduling")
            print("Install with: pip install schedule")
            print("\nYou can still use --run-once option for manual execution")
            return

        print("\n" + "=" * 60)
        print("Session Report Scheduler Started")
        print("=" * 60)
        print(f"Config file: {self.config_file}")
        print("Press Ctrl+C to stop")
        print("=" * 60 + "\n")

        self.setup_schedule()

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
        except KeyboardInterrupt:
            print("\n[SCHEDULER] Stopped by user")

    def run_once(self, period: str = "weekly") -> None:
        """단일 실행 (테스트/수동 실행용)"""
        if period == "daily":
            self.generate_daily_report()
        elif period == "weekly":
            self.generate_weekly_report()
        elif period == "monthly":
            self.generate_monthly_report()
        else:
            print(f"[ERROR] Unknown period: {period}")

    def setup_windows_task(self) -> None:
        """Windows Task Scheduler 설정"""
        if platform.system() != "Windows":
            print("[ERROR] This command is only for Windows")
            return

        script_path = Path(__file__).absolute()
        python_path = sys.executable

        # 주간 작업 생성
        task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Session Report Weekly Generator</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2025-01-01T09:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByWeek>
        <DaysOfWeek>
          <Monday />
        </DaysOfWeek>
        <WeeksInterval>1</WeeksInterval>
      </ScheduleByWeek>
    </CalendarTrigger>
  </Triggers>
  <Actions Context="Author">
    <Exec>
      <Command>{python_path}</Command>
      <Arguments>"{script_path}" --run-once --period weekly</Arguments>
      <WorkingDirectory>{script_path.parent}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

        # 임시 XML 파일 생성
        temp_xml = Path("temp_task.xml")
        with open(temp_xml, "w", encoding="utf-16") as f:
            f.write(task_xml)

        try:
            # schtasks 명령 실행
            result = subprocess.run(
                ["schtasks", "/create", "/tn", "SessionReportWeekly", "/xml", str(temp_xml), "/f"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("[SUCCESS] Windows Task created: SessionReportWeekly")
                print("You can manage it in Task Scheduler")
            else:
                print(f"[ERROR] Failed to create task: {result.stderr}")

        finally:
            # 임시 파일 삭제
            if temp_xml.exists():
                temp_xml.unlink()

    def setup_cron_job(self) -> None:
        """Linux/Mac cron job 설정"""
        if platform.system() == "Windows":
            print("[ERROR] This command is for Linux/Mac only")
            return

        script_path = Path(__file__).absolute()
        python_path = sys.executable

        cron_line = f"0 9 * * 1 {python_path} {script_path} --run-once --period weekly"

        print("Add this line to your crontab (crontab -e):")
        print(cron_line)
        print("\nThis will run the weekly report every Monday at 9:00 AM")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="Schedule automatic session report generation")
    parser.add_argument("--run-once", action="store_true", help="Run once and exit")
    parser.add_argument(
        "--period", choices=["daily", "weekly", "monthly"], default="weekly", help="Report period for run-once mode"
    )
    parser.add_argument(
        "--schedule", choices=["daily", "weekly", "monthly", "all"], help="Run scheduler with specified schedule"
    )
    parser.add_argument("--setup-windows-task", action="store_true", help="Setup Windows Task Scheduler")
    parser.add_argument("--setup-cron", action="store_true", help="Show cron job setup instructions")
    parser.add_argument("--config", type=str, default="config/report_scheduler.json", help="Configuration file path")

    args = parser.parse_args()

    scheduler = SessionReportScheduler(config_file=args.config)

    if args.setup_windows_task:
        scheduler.setup_windows_task()
    elif args.setup_cron:
        scheduler.setup_cron_job()
    elif args.run_once:
        scheduler.run_once(period=args.period)
    elif args.schedule:
        # 특정 스케줄만 활성화
        if args.schedule != "all":
            for key in scheduler.config["schedules"]:
                scheduler.config["schedules"][key]["enabled"] = key == args.schedule
        scheduler.run_scheduler()
    else:
        # 기본: 설정된 모든 스케줄 실행
        scheduler.run_scheduler()


if __name__ == "__main__":
    main()
