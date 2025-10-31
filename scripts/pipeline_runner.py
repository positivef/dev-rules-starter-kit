#!/usr/bin/env python3
"""
Pipeline Runner for 7-Layer Architecture Automation
Executes the Constitution enforcement pipeline defined in config/pipeline.yaml
"""

import json
import logging
import subprocess
import time
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("RUNS/pipeline.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Result from tool execution"""

    tool_name: str
    layer_id: int
    success: bool
    output: str
    error: Optional[str] = None
    duration_seconds: float = 0.0
    metrics: Dict[str, Any] = None


@dataclass
class LayerResult:
    """Result from layer execution"""

    layer_id: int
    layer_name: str
    success: bool
    tools_results: List[ToolResult]
    duration_seconds: float

    @property
    def failed_tools(self) -> List[str]:
        return [r.tool_name for r in self.tools_results if not r.success]


class PipelineRunner:
    """Executes the 7-layer architecture pipeline"""

    def __init__(self, config_file: Path = Path("config/pipeline.yaml")):
        self.config_file = config_file
        self.config = self._load_config()
        self.state = {}
        self.results = {}

    def _load_config(self) -> Dict:
        """Load pipeline configuration"""
        with open(self.config_file, "r") as f:
            return yaml.safe_load(f)

    def _save_state(self):
        """Save pipeline state for recovery"""
        state_file = Path(self.config["execution"]["state_file"])
        state_file.parent.mkdir(parents=True, exist_ok=True)

        with open(state_file, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "results": {k: v.__dict__ for k, v in self.results.items()},
                    "completed_layers": list(self.results.keys()),
                },
                f,
                indent=2,
                default=str,
            )

    def _execute_tool(self, tool: Dict, layer_id: int) -> ToolResult:
        """Execute a single tool"""
        start_time = time.time()
        tool_name = tool["name"]

        logger.info(f"[Layer {layer_id}] Executing {tool_name}")

        try:
            # Build command
            cmd = ["python", tool["script"]]
            if "args" in tool:
                cmd.extend(tool["args"])

            # Execute
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.config["execution"]["timeout_seconds"])

            duration = time.time() - start_time

            # Parse metrics from output if available
            metrics = self._parse_metrics(result.stdout)

            return ToolResult(
                tool_name=tool_name,
                layer_id=layer_id,
                success=(result.returncode == 0),
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                duration_seconds=duration,
                metrics=metrics,
            )

        except subprocess.TimeoutExpired:
            logger.error(f"[Layer {layer_id}] {tool_name} timed out")
            return ToolResult(
                tool_name=tool_name,
                layer_id=layer_id,
                success=False,
                output="",
                error="Tool execution timed out",
                duration_seconds=time.time() - start_time,
            )
        except Exception as e:
            logger.error(f"[Layer {layer_id}] {tool_name} failed: {e}")
            return ToolResult(
                tool_name=tool_name,
                layer_id=layer_id,
                success=False,
                output="",
                error=str(e),
                duration_seconds=time.time() - start_time,
            )

    def _parse_metrics(self, output: str) -> Dict[str, Any]:
        """Parse metrics from tool output"""
        metrics = {}

        # Parse common metrics patterns
        if "Pass Rate:" in output:
            try:
                pass_rate = float(output.split("Pass Rate:")[1].split("%")[0].strip())
                metrics["pass_rate"] = pass_rate
            except (ValueError, IndexError, AttributeError):
                pass  # Continue if parsing fails

        if "Security Issues" in output and "|" in output:
            try:
                for line in output.split("\n"):
                    if "Security Issues" in line and "|" in line:
                        parts = line.split("|")
                        if len(parts) > 2:
                            count = int(parts[2].strip())
                            metrics["security_issues"] = count
                            break
            except (ValueError, IndexError, AttributeError):
                pass  # Continue if parsing fails

        if "Orphaned entries:" in output:
            try:
                orphaned = int(output.split("Orphaned entries:")[1].split()[0])
                metrics["orphaned_entries"] = orphaned
            except (ValueError, IndexError, AttributeError):
                pass  # Continue if parsing fails

        return metrics

    def _check_dependencies(self, layer: Dict) -> bool:
        """Check if layer dependencies are satisfied"""
        if "dependencies" not in layer:
            return True

        for dep_id in layer["dependencies"]:
            if dep_id not in self.results:
                logger.warning(f"Dependency layer {dep_id} not completed")
                return False
            if not self.results[dep_id].success:
                logger.warning(f"Dependency layer {dep_id} failed")
                return False

        return True

    def _execute_layer(self, layer: Dict) -> LayerResult:
        """Execute all tools in a layer"""
        layer_id = layer["id"]
        layer_name = layer["name"]
        start_time = time.time()

        logger.info(f"[Layer {layer_id}] Starting {layer_name}")

        # Check dependencies
        if not self._check_dependencies(layer):
            return LayerResult(layer_id=layer_id, layer_name=layer_name, success=False, tools_results=[], duration_seconds=0)

        # Apply delay if specified
        if "delay_seconds" in layer:
            time.sleep(layer["delay_seconds"])

        # Execute tools
        tools_results = []

        if layer.get("parallel", False):
            # Execute tools in parallel
            with ThreadPoolExecutor(max_workers=self.config["execution"]["max_parallel"]) as executor:
                futures = {executor.submit(self._execute_tool, tool, layer_id): tool for tool in layer["tools"]}

                for future in as_completed(futures):
                    tools_results.append(future.result())
        else:
            # Execute tools sequentially
            for tool in layer["tools"]:
                result = self._execute_tool(tool, layer_id)
                tools_results.append(result)

                # Stop on failure unless optional
                if not result.success and not tool.get("optional", False):
                    if not layer.get("always_run", False):
                        break

        # Determine layer success
        required_tools = [t for t in layer["tools"] if not t.get("optional", False)]
        required_results = [r for r in tools_results if r.tool_name in [t["name"] for t in required_tools]]
        layer_success = all(r.success for r in required_results) or layer.get("optional", False)

        duration = time.time() - start_time

        return LayerResult(
            layer_id=layer_id,
            layer_name=layer_name,
            success=layer_success,
            tools_results=tools_results,
            duration_seconds=duration,
        )

    def _check_quality_gates(self) -> List[Dict]:
        """Check quality gates against metrics"""
        failed_gates = []

        for gate in self.config["quality_gates"]:
            # Extract source layer and tool
            source_parts = gate["source"].split(".")
            layer_name = source_parts[0]
            tool_name = source_parts[1] if len(source_parts) > 1 else None

            # Find the metric value
            metric_value = None
            for layer_id, result in self.results.items():
                if f"layer_{layer_id}" == layer_name or result.layer_name == layer_name:
                    for tool_result in result.tools_results:
                        if tool_name is None or tool_result.tool_name == tool_name:
                            if tool_result.metrics and gate["metric"] in tool_result.metrics:
                                metric_value = tool_result.metrics[gate["metric"]]
                                break

            if metric_value is None:
                logger.warning(f"Quality gate '{gate['name']}' metric not found")
                continue

            # Check threshold
            threshold = gate["threshold"]
            operator = gate["operator"]

            passed = False
            if operator == ">=":
                passed = metric_value >= threshold
            elif operator == "<=":
                passed = metric_value <= threshold
            elif operator == "==":
                passed = metric_value == threshold
            elif operator == ">":
                passed = metric_value > threshold
            elif operator == "<":
                passed = metric_value < threshold

            if not passed:
                failed_gates.append(
                    {
                        "name": gate["name"],
                        "metric": gate["metric"],
                        "actual": metric_value,
                        "threshold": threshold,
                        "operator": operator,
                    }
                )

        return failed_gates

    def _rollback(self):
        """Execute rollback strategy"""
        if not self.config["rollback"]["enabled"]:
            return

        logger.warning("Executing rollback strategy")

        for action in self.config["rollback"]["actions"]:
            try:
                # Parse command safely without shell=True (P5 security compliance)
                if isinstance(action, str):
                    # Split command into parts for safe execution
                    cmd_parts = action.split()
                    subprocess.run(cmd_parts, check=True)
                else:
                    # If action is already a list, use directly
                    subprocess.run(action, check=True)
                logger.info(f"Rollback action completed: {action}")
            except Exception as e:
                logger.error(f"Rollback action failed: {action} - {e}")

    def run(self, start_layer: int = 1) -> bool:
        """Run the pipeline"""
        logger.info("=" * 60)
        logger.info(f"Starting {self.config['pipeline_name']} v{self.config['version']}")
        logger.info("=" * 60)

        overall_success = True

        # Execute layers in order
        for layer in self.config["layers"]:
            if layer["id"] < start_layer:
                continue

            result = self._execute_layer(layer)
            self.results[layer["id"]] = result

            # Save state after each layer
            if self.config["execution"]["save_state"]:
                self._save_state()

            # Log results
            if result.success:
                logger.info(
                    f"[Layer {layer['id']}] {layer['name']} completed successfully " f"({result.duration_seconds:.1f}s)"
                )
            else:
                logger.error(f"[Layer {layer['id']}] {layer['name']} FAILED " f"({result.duration_seconds:.1f}s)")
                logger.error(f"Failed tools: {result.failed_tools}")

                # Check if we should continue
                if not self.config["execution"]["continue_on_failure"]:
                    if not layer.get("always_run", False):
                        overall_success = False

                        # Check if rollback needed
                        if layer["id"] in self.config["rollback"].get("on_failure_at_layers", []):
                            self._rollback()
                        break

        # Check quality gates
        failed_gates = self._check_quality_gates()
        if failed_gates:
            logger.error(f"Quality gates failed: {failed_gates}")
            overall_success = False

            for gate in failed_gates:
                logger.error(f"[QUALITY] {gate['name']}: {gate['actual']} " f"{gate['operator']} {gate['threshold']} FAILED")

        # Final report
        logger.info("=" * 60)
        if overall_success:
            logger.info("[SUCCESS] Pipeline completed successfully")
            self._notify("on_success")
        else:
            logger.error("[FAILURE] Pipeline failed")
            self._notify("on_failure")

        # Generate summary
        self._generate_summary()

        return overall_success

    def _notify(self, event: str):
        """Send notifications"""
        notifications = self.config["notifications"].get(event, [])

        for notification in notifications:
            if notification["type"] == "log":
                level = notification.get("level", "info")
                message = notification["message"]

                # Format message with context
                if "{layer_id}" in message:
                    # Find failed layer
                    for layer_id, result in self.results.items():
                        if not result.success:
                            message = message.replace("{layer_id}", str(layer_id))
                            break

                getattr(logger, level)(message)

    def _generate_summary(self):
        """Generate execution summary"""
        summary = []
        summary.append("\n" + "=" * 60)
        summary.append("PIPELINE EXECUTION SUMMARY")
        summary.append("=" * 60)

        total_duration = sum(r.duration_seconds for r in self.results.values())
        successful_layers = sum(1 for r in self.results.values() if r.success)

        summary.append(f"Total layers executed: {len(self.results)}/{len(self.config['layers'])}")
        summary.append(f"Successful layers: {successful_layers}")
        summary.append(f"Total duration: {total_duration:.1f} seconds")

        summary.append("\nLayer Results:")
        for layer_id, result in self.results.items():
            status = "[OK] PASS" if result.success else "[FAIL] FAIL"
            summary.append(f"  Layer {layer_id} ({result.layer_name}): {status} " f"({result.duration_seconds:.1f}s)")

            for tool_result in result.tools_results:
                tool_status = "✓" if tool_result.success else "✗"
                summary.append(f"    {tool_status} {tool_result.tool_name} " f"({tool_result.duration_seconds:.1f}s)")

        # Save summary
        summary_file = Path("RUNS/pipeline_summary.txt")
        summary_file.parent.mkdir(parents=True, exist_ok=True)

        with open(summary_file, "w") as f:
            f.write("\n".join(summary))

        # Print summary
        print("\n".join(summary))


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="7-Layer Architecture Pipeline Runner")
    parser.add_argument("--config", default="config/pipeline.yaml", help="Pipeline configuration file")
    parser.add_argument("--start-layer", type=int, default=1, help="Start from specific layer (for recovery)")
    parser.add_argument("--dry-run", action="store_true", help="Show execution plan without running")

    args = parser.parse_args()

    if args.dry_run:
        # Just show the plan
        with open(args.config, "r") as f:
            config = yaml.safe_load(f)

        print("Pipeline Execution Plan:")
        print("=" * 40)
        for layer in config["layers"]:
            print(f"Layer {layer['id']}: {layer['name']}")
            for tool in layer["tools"]:
                optional = " (optional)" if tool.get("optional", False) else ""
                print(f"  - {tool['name']}{optional}")
        return 0

    # Run pipeline
    runner = PipelineRunner(Path(args.config))
    success = runner.run(start_layer=args.start_layer)

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
