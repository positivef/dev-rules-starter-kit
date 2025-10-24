"""OS-specific Performance Configuration for Tier 1 Integration System.

Provides realistic performance thresholds based on operating system.
"""

import platform
from typing import Dict


class PerformanceConfig:
    """Manages OS-specific performance configurations."""

    @staticmethod
    def get_os_type() -> str:
        """Get simplified OS type.

        Returns:
            'windows', 'linux', 'darwin', or 'unknown'.
        """
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system == "linux":
            return "linux"
        elif system == "darwin":
            return "darwin"
        else:
            return "unknown"

    @staticmethod
    def get_thresholds() -> Dict[str, Dict[str, float]]:
        """Get OS-specific performance thresholds.

        Returns:
            Dictionary of performance thresholds by category.
        """
        os_type = PerformanceConfig.get_os_type()

        # Base thresholds for Linux (optimal performance)
        base_thresholds = {
            "cache_operations": {
                "lookup_ms": 2.0,
                "write_ms": 5.0,
                "bulk_write_s": 4.0,
                "ttl_check_ms": 1.0,
            },
            "file_operations": {
                "read_small_ms": 5.0,
                "read_large_ms": 50.0,
                "write_small_ms": 10.0,
                "write_large_ms": 100.0,
                "list_directory_ms": 20.0,
            },
            "parallel_processing": {
                "thread_spawn_ms": 5.0,
                "process_spawn_ms": 50.0,
                "queue_operation_ms": 2.0,
                "lock_acquire_ms": 1.0,
            },
            "network_operations": {
                "local_api_call_ms": 50.0,
                "webhook_send_ms": 200.0,
                "health_check_ms": 100.0,
            },
            "database_operations": {
                "query_simple_ms": 10.0,
                "query_complex_ms": 100.0,
                "insert_single_ms": 20.0,
                "bulk_insert_ms": 500.0,
            },
        }

        # Apply OS-specific multipliers
        multipliers = {
            "windows": {
                "cache_operations": 3.0,  # Windows has slower I/O
                "file_operations": 2.5,
                "parallel_processing": 2.0,
                "network_operations": 1.2,
                "database_operations": 1.5,
            },
            "darwin": {
                "cache_operations": 1.5,  # macOS is between Linux and Windows
                "file_operations": 1.5,
                "parallel_processing": 1.3,
                "network_operations": 1.1,
                "database_operations": 1.2,
            },
            "linux": {
                # Linux uses base thresholds (multiplier = 1.0)
                "cache_operations": 1.0,
                "file_operations": 1.0,
                "parallel_processing": 1.0,
                "network_operations": 1.0,
                "database_operations": 1.0,
            },
            "unknown": {
                # Conservative thresholds for unknown OS
                "cache_operations": 5.0,
                "file_operations": 3.0,
                "parallel_processing": 2.5,
                "network_operations": 1.5,
                "database_operations": 2.0,
            },
        }

        # Apply multipliers
        os_multipliers = multipliers.get(os_type, multipliers["unknown"])
        adjusted_thresholds = {}

        for category, thresholds in base_thresholds.items():
            multiplier = os_multipliers.get(category, 1.0)
            adjusted_thresholds[category] = {key: value * multiplier for key, value in thresholds.items()}

        return adjusted_thresholds

    @staticmethod
    def get_threshold(category: str, operation: str) -> float:
        """Get specific threshold value.

        Args:
            category: Performance category (e.g., 'cache_operations').
            operation: Specific operation (e.g., 'lookup_ms').

        Returns:
            Threshold value in appropriate units.
        """
        thresholds = PerformanceConfig.get_thresholds()
        return thresholds.get(category, {}).get(operation, 1000.0)  # Default to 1 second

    @staticmethod
    def get_parallel_workers() -> int:
        """Get recommended number of parallel workers for this OS.

        Returns:
            Number of recommended workers.
        """
        import multiprocessing

        cpu_count = multiprocessing.cpu_count()
        os_type = PerformanceConfig.get_os_type()

        # OS-specific worker recommendations
        if os_type == "windows":
            # Windows has more overhead for process creation
            return max(1, cpu_count // 2)
        elif os_type == "darwin":
            # macOS handles parallelism well
            return max(1, cpu_count - 1)
        elif os_type == "linux":
            # Linux is optimal for parallelism
            return cpu_count
        else:
            # Conservative for unknown OS
            return max(1, cpu_count // 2)

    @staticmethod
    def get_timeout_multiplier() -> float:
        """Get timeout multiplier for this OS.

        Returns:
            Multiplier for timeout values.
        """
        os_type = PerformanceConfig.get_os_type()
        multipliers = {
            "windows": 2.0,  # Windows needs longer timeouts
            "darwin": 1.5,
            "linux": 1.0,
            "unknown": 3.0,
        }
        return multipliers.get(os_type, 3.0)

    @staticmethod
    def format_report() -> str:
        """Generate a performance configuration report.

        Returns:
            Formatted report string.
        """
        os_type = PerformanceConfig.get_os_type()
        thresholds = PerformanceConfig.get_thresholds()
        workers = PerformanceConfig.get_parallel_workers()
        timeout_mult = PerformanceConfig.get_timeout_multiplier()

        report = []
        report.append("=" * 60)
        report.append("Performance Configuration Report")
        report.append("=" * 60)
        report.append(f"Operating System: {platform.system()} ({os_type})")
        report.append(f"CPU Cores: {platform.processor() or 'Unknown'}")
        report.append(f"Recommended Workers: {workers}")
        report.append(f"Timeout Multiplier: {timeout_mult}x")
        report.append("")

        report.append("Performance Thresholds:")
        report.append("-" * 60)

        for category, ops in thresholds.items():
            report.append(f"\n{category.replace('_', ' ').title()}:")
            for op, value in ops.items():
                unit = "ms" if op.endswith("_ms") else "s" if op.endswith("_s") else ""
                op_name = op.replace("_ms", "").replace("_s", "").replace("_", " ").title()
                report.append(f"  {op_name:30} : {value:8.1f}{unit}")

        report.append("=" * 60)
        return "\n".join(report)


def main():
    """Display performance configuration for current system."""
    print(PerformanceConfig.format_report())


if __name__ == "__main__":
    main()
