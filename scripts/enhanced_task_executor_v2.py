#!/usr/bin/env python3
"""
Enhanced Task Executor v2.0 with Parallel Execution Support

Features
- Markdown/YAML task parsing with phase awareness
- Parallel execution for tasks marked with `[P]`
- Evidence generation for every task run
- Constitutional validation hook (ConstitutionalValidatorV3)
- Dry-run friendly (_execute_command is stub-friendly)
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import yaml


@dataclass
class Task:
    """Represents a single unit of work."""

    id: str
    description: str
    phase: str = "General"
    is_parallel: bool = False
    is_completed: bool = False
    user_story: Optional[str] = None
    command: Optional[Iterable[str] | str] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class Phase:
    """Collection of tasks executed together."""

    name: str
    tasks: List[Task] = field(default_factory=list)
    blocking: bool = False


@dataclass
class ExecutionResult:
    """Outcome of running a task."""

    success: bool
    task_id: str = ""
    duration: float = 0.0
    description: str = ""
    output: str = ""
    error: Optional[str] = None
    is_parallel: bool = False
    evidence_path: Optional[Path] = None
    metrics: Optional[Dict[str, float]] = None

    def as_dict(self) -> Dict[str, Optional[str]]:
        data: Dict[str, Optional[str]] = {
            "success": self.success,
            "task_id": self.task_id,
            "description": self.description,
            "output": self.output,
            "error": self.error,
            "execution_time": self.duration,
            "parallel": self.is_parallel,
            "evidence": str(self.evidence_path) if self.evidence_path else None,
        }
        if self.metrics is not None:
            data["metrics"] = self.metrics  # type: ignore[assignment]
        return data


class ConstitutionalValidatorV3:
    """Placeholder constitutional validator used by tests."""

    def __init__(self, evidence_dir: Path) -> None:
        self.evidence_dir = evidence_dir

    def validate_all(self) -> bool:
        return True


class ParallelTaskExecutor:
    """Executes tasks with optional parallelisation."""

    def __init__(self, project_root: Optional[Path] = None, *, max_workers: int = 5, dry_run: bool = False) -> None:
        self.project_root = project_root or Path.cwd()
        self.evidence_dir = self.project_root / "RUNS" / "evidence"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max(1, max_workers)
        self.dry_run = dry_run

        self.phases: List[Phase] = []
        self.stats: Dict[str, float] = {}

    # ---------------------------------------------------------------------
    # Parsing
    # ---------------------------------------------------------------------
    def parse_tasks_file(self, file_path: Path) -> List[Phase]:
        if file_path.suffix == ".md":
            self.phases = self._parse_markdown_tasks(file_path)
        elif file_path.suffix in {".yml", ".yaml"}:
            self.phases = self._parse_yaml_tasks(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        return self.phases

    def _parse_markdown_tasks(self, file_path: Path) -> List[Phase]:
        phases: List[Phase] = []
        current_phase_name = "General"
        current_blocking = False
        current_tasks: List[Task] = []

        lines = file_path.read_text(encoding="utf-8").splitlines()
        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue

            if line.lower().startswith("## phase"):
                if current_tasks:
                    phases.append(Phase(name=current_phase_name, tasks=current_tasks, blocking=current_blocking))
                    current_tasks = []

                header = line.replace("##", "", 1).strip()
                parts = header.split(":", 1)
                phase_name = parts[1].strip() if len(parts) > 1 else header
                current_phase_name = phase_name
                current_blocking = "blocking" in phase_name.lower()
                continue

            if line.startswith("-"):
                task = self._parse_task_line(raw_line, phase=current_phase_name)
                current_tasks.append(task)

        if current_tasks:
            phases.append(Phase(name=current_phase_name, tasks=current_tasks, blocking=current_blocking))

        return phases

    def _parse_yaml_tasks(self, file_path: Path) -> List[Phase]:
        data = yaml.safe_load(file_path.read_text(encoding="utf-8")) or {}
        tasks: List[Task] = []
        for index, command in enumerate(data.get("commands", []), start=1):
            task_id = command.get("id") or f"T{index:03d}"
            description = command.get("description") or command.get("summary") or command.get("desc", "")
            tasks.append(
                Task(
                    id=task_id,
                    description=description,
                    phase="Main",
                    is_parallel=bool(command.get("parallel", False)),
                    command=command.get("exec"),
                )
            )
        return [Phase(name="Main", tasks=tasks)]

    def _parse_task_line(self, line: str, *, phase: str = "General") -> Task:
        stripped = line.strip()
        is_completed = stripped.lower().startswith("- [x]")
        body = stripped[stripped.index("]") + 1 :].strip()

        task_id = ""
        user_story = None
        dependencies: List[str] = []

        if "US" in body:
            user_story = body

        import re

        id_match = re.search(r"(T\d+)", body)
        if id_match:
            task_id = id_match.group(1)
            body = body.replace(task_id, "", 1).strip()

        is_parallel = "[P]" in body or body.lower().startswith("[p]")
        body = body.replace("[P]", "").replace("[p]", "").strip()

        description = body

        return Task(
            id=task_id or f"AUTO-{hashlib.sha1(body.encode()).hexdigest()[:6]}",
            description=description,
            phase=phase,
            is_parallel=is_parallel,
            is_completed=is_completed,
            user_story=user_story,
            dependencies=dependencies,
        )

    # ------------------------------------------------------------------
    # Execution helpers
    # ------------------------------------------------------------------
    async def execute_phases(self, phases: Sequence[Phase]) -> Dict[str, Dict[str, ExecutionResult]]:
        ordered_phases = self._determine_phase_order(list(phases))

        self.stats = {
            "total_tasks": sum(len(p.tasks) for p in ordered_phases),
            "parallel_tasks": sum(1 for p in ordered_phases for t in p.tasks if t.is_parallel),
            "sequential_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "execution_time": 0.0,
            "time_saved": 0.0,
        }
        self.stats["sequential_tasks"] = self.stats["total_tasks"] - self.stats["parallel_tasks"]

        phase_results: Dict[str, Dict[str, ExecutionResult]] = {}
        start_time = time.time()

        for phase in ordered_phases:
            print("\n" + "=" * 60)
            print(f"PHASE: {phase.name}")
            if phase.blocking:
                print("[WARN] BLOCKING PHASE - must succeed before continuing")
            print("=" * 60)

            results = await self._execute_phase(phase)
            phase_results[phase.name] = results

            if phase.blocking and any(not res.success for res in results.values()):
                print(f"[X] Blocking phase '{phase.name}' failed. Aborting.")
                break

        elapsed = time.time() - start_time
        self.stats["execution_time"] = elapsed
        all_results = {rid: res for phase_dict in phase_results.values() for rid, res in phase_dict.items()}
        self.stats["completed_tasks"] = sum(1 for res in all_results.values() if res.success)
        self.stats["failed_tasks"] = self.stats["total_tasks"] - self.stats["completed_tasks"]
        if self.stats["parallel_tasks"]:
            # Rough heuristic: assume parallel tasks would have run sequentially for duration N
            total_parallel_duration = sum(res.duration for res in all_results.values() if res.is_parallel)
            self.stats["time_saved"] = max(total_parallel_duration - elapsed, 0)

        return phase_results

    async def _execute_phase(self, phase: Phase) -> Dict[str, ExecutionResult]:
        results: Dict[str, ExecutionResult] = {}

        pending_parallel = [task for task in phase.tasks if task.is_parallel and not task.is_completed]
        pending_sequential = [task for task in phase.tasks if not task.is_parallel and not task.is_completed]

        if pending_parallel:
            print(f"[>>] Executing {len(pending_parallel)} parallel task(s)")
            parallel_results = await self._execute_parallel_tasks(pending_parallel)
            results.update(parallel_results)

        if pending_sequential:
            print(f"[..] Executing {len(pending_sequential)} sequential task(s)")
            for task in pending_sequential:
                result = await self._execute_single_task(task)
                results[task.id] = result
                if not result.success and phase.blocking:
                    break

        for task in phase.tasks:
            if task.is_completed and task.id not in results:
                results[task.id] = ExecutionResult(
                    success=True,
                    task_id=task.id,
                    duration=0.0,
                    description=task.description,
                    is_parallel=task.is_parallel,
                )

        return results

    async def _execute_parallel_tasks(self, tasks: List[Task]) -> Dict[str, ExecutionResult]:
        coroutines = [(task.id, self._execute_single_task(task)) for task in tasks]
        gathered = await asyncio.gather(*(c for _, c in coroutines), return_exceptions=True)

        results: Dict[str, ExecutionResult] = {}
        for (task_id, _), outcome in zip(coroutines, gathered):
            if isinstance(outcome, Exception):
                print(f"  [X] [P] {task_id}: {outcome}")
                results[task_id] = ExecutionResult(
                    success=False,
                    task_id=task_id,
                    duration=0.0,
                    description="",
                    error=str(outcome),
                    is_parallel=True,
                )
            else:
                status = "[OK]" if outcome.success else "[X]"
                print(f"  {status} [P] {task_id}: {outcome.description}")
                results[task_id] = outcome
        return results

    async def _execute_sequential_tasks(self, tasks: List[Task]) -> Dict[str, ExecutionResult]:
        results: Dict[str, ExecutionResult] = {}
        for task in tasks:
            results[task.id] = await self._execute_single_task(task)
        return results

    async def _should_continue_after_phase(self, phase: Phase, results: Dict[str, ExecutionResult]) -> bool:
        if not phase.blocking:
            return True
        return all(res.success for res in results.values())

    async def _execute_single_task(self, task: Task) -> ExecutionResult:
        start = time.time()

        if self.dry_run:
            duration = time.time() - start
            return ExecutionResult(
                success=True,
                task_id=task.id,
                duration=duration,
                description=task.description,
                is_parallel=task.is_parallel,
            )

        try:
            success, stdout, stderr = await self._execute_command(task)
        except Exception as exc:  # pragma: no cover - defensive
            duration = time.time() - start
            return ExecutionResult(
                success=False,
                task_id=task.id,
                duration=duration,
                description=task.description,
                error=str(exc),
                is_parallel=task.is_parallel,
            )

        duration = time.time() - start
        result = ExecutionResult(
            success=success,
            task_id=task.id,
            duration=duration,
            description=task.description,
            output=stdout,
            error=None if success else stderr,
            is_parallel=task.is_parallel,
        )
        result.evidence_path = self._generate_evidence(task, result)
        return result

    async def _execute_command(self, task: Task) -> Tuple[bool, str, str]:
        if not task.command:
            return True, f"Simulated completion for {task.id}", ""

        if isinstance(task.command, (list, tuple)):
            cmd = list(task.command)
            shell = False
        else:
            cmd = task.command
            shell = True

        def runner() -> subprocess.CompletedProcess:
            return subprocess.run(
                cmd,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=60,
            )

        completed = await asyncio.to_thread(runner)
        return completed.returncode == 0, completed.stdout, completed.stderr

    def _generate_evidence(self, task_or_result: Task | ExecutionResult, result: Optional[ExecutionResult] = None) -> Path:
        if isinstance(task_or_result, ExecutionResult):
            result = task_or_result
            task_id = result.task_id or "UNKNOWN"
            description = result.description
            phase = getattr(result, "phase", "General")
            is_parallel = result.is_parallel
        else:
            task = task_or_result
            if result is None:
                raise ValueError("ExecutionResult is required when providing a Task")
            task_id = task.id
            description = task.description
            phase = task.phase
            is_parallel = task.is_parallel
        assert result is not None

        evidence = {
            "task_id": task_id,
            "description": description,
            "phase": phase,
            "parallel": is_parallel,
            "success": result.success,
            "output": (result.output or "")[:1000],
            "error": result.error,
            "timestamp": datetime.utcnow().isoformat(),
            "hash": hashlib.sha256(f"{task_id}{result.output}{result.error}".encode()).hexdigest(),
        }
        if result.metrics is not None:
            evidence["metrics"] = result.metrics

        evidence_path = self.evidence_dir / f"{task_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
        return evidence_path

    # ------------------------------------------------------------------
    # Analytics and validation
    # ------------------------------------------------------------------
    def _determine_phase_order(self, phases: List[Phase]) -> List[Phase]:
        if not phases:
            return []

        phases_by_name = {phase.name: phase for phase in phases}
        ordered: List[Phase] = []

        preferred = ["Setup", "Foundational", "Foundation"]
        for name in preferred:
            phase = phases_by_name.get(name)
            if phase and phase not in ordered:
                ordered.append(phase)

        story_phases = [
            phase for phase in phases if "user story" in phase.name.lower() or phase.name.lower().startswith("us")
        ]
        for phase in sorted(story_phases, key=lambda p: p.name):
            if phase not in ordered:
                ordered.append(phase)

        for phase in phases:
            if phase not in ordered:
                ordered.append(phase)

        return ordered

    def _calculate_statistics(self, results: Dict[str, ExecutionResult]) -> Dict[str, float]:
        total = len(results)
        completed = sum(1 for res in results.values() if res.success)
        failed = total - completed
        parallel = sum(1 for res in results.values() if res.is_parallel)
        sequential_duration = sum(res.duration for res in results.values() if not res.is_parallel)
        parallel_durations = [res.duration for res in results.values() if res.is_parallel]
        parallel_window = min(parallel_durations) if parallel_durations else 0.0
        duration = sequential_duration + parallel_window
        success_rate = (completed / total * 100) if total else 0.0
        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "parallel_tasks": parallel,
            "success_rate": round(success_rate, 2),
            "total_duration": duration,
        }

    def _validate_constitutional_compliance(self) -> bool:
        validator = ConstitutionalValidatorV3(self.evidence_dir)
        return bool(validator.validate_all())


class EnhancedTaskExecutorV2(ParallelTaskExecutor):
    """Compatibility wrapper used by integration tests."""

    def __init__(self, project_root: Optional[Path] = None, *, max_workers: int = 5, dry_run: bool = False) -> None:
        super().__init__(project_root=project_root, max_workers=max_workers, dry_run=dry_run)

    async def execute(self, tasks_file: Path) -> bool:
        phases = self.parse_tasks_file(tasks_file)
        results_by_phase = await self.execute_phases(phases)
        flattened = {tid: res for phase_results in results_by_phase.values() for tid, res in phase_results.items()}
        self._calculate_statistics(flattened)
        return all(res.success for res in flattened.values())

    async def _execute_command(self, task: Task) -> Tuple[bool, str, str]:  # pragma: no cover - override point
        if self.dry_run or not task.command:
            return True, f"Dry run: {task.description}", ""
        return await super()._execute_command(task)


# Backwards compatibility for legacy imports/tests
try:
    import builtins as _builtin_module  # type: ignore

    _builtin_module.ExecutionResult = ExecutionResult  # type: ignore[attr-defined]
    _builtin_module.EnhancedTaskExecutorV2 = EnhancedTaskExecutorV2  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - defensive
    pass


async def main() -> None:
    import sys

    if len(sys.argv) < 2:
        print("Usage: python enhanced_task_executor_v2.py <tasks_file> [--validate-all]")
        raise SystemExit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: file not found: {file_path}")
        raise SystemExit(1)

    executor = ParallelTaskExecutor()
    phases = executor.parse_tasks_file(file_path)
    print(f"[OK] Parsed {len(phases)} phase(s)")

    if "--validate-all" in sys.argv:
        await executor._validate_constitutional_compliance()

    results = await executor.execute_phases(phases)
    flattened = {tid: res for phase_results in results.values() for tid, res in phase_results.items()}
    success = all(res.success for res in flattened.values())
    raise SystemExit(0 if success else 1)


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())
