"""Demo script to showcase Phase C integration

This script demonstrates:
1. Critical file detection (matches *_executor.py pattern)
2. Cache usage
3. Evidence logging with Phase C metadata

To test:
1. Run dev_assistant.py
2. Modify this file
3. Save it
4. Check console output for Phase C features
"""


def execute_task(task_name: str) -> str:
    """Execute a task (demo function)

    Args:
        task_name: Name of the task to execute

    Returns:
        Task result message
    """
    return f"Executing task: {task_name}"


if __name__ == "__main__":
    result = execute_task("demo")
    print(result)
