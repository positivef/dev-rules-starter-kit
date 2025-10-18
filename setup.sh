#!/bin/bash
# setup.sh - Bash wrapper for setup.py
# Cross-platform project initialization script

set -e  # Exit on error

# Colors for output (optional, works on Unix-like systems)
if command -v tput > /dev/null 2>&1 && [ -t 1 ]; then
    RED=$(tput setaf 1)
    GREEN=$(tput setaf 2)
    YELLOW=$(tput setaf 3)
    RESET=$(tput sgr0)
else
    RED=""
    GREEN=""
    YELLOW=""
    RESET=""
fi

# Check if Python is available
if ! command -v python3 > /dev/null 2>&1 && ! command -v python > /dev/null 2>&1; then
    echo "${RED}[ERROR] Python is not installed or not in PATH${RESET}" >&2
    echo "Please install Python 3.10+ from https://www.python.org/downloads/" >&2
    exit 1
fi

# Determine Python command
if command -v python3 > /dev/null 2>&1; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# Display banner
echo "============================================="
echo "${GREEN}Dev Rules Starter Kit Setup${RESET}"
echo "============================================="
echo

# Check if requirements are met
if [ ! -f "setup.py" ]; then
    echo "${RED}[ERROR] setup.py not found${RESET}" >&2
    echo "Please run this script from the dev-rules-starter-kit directory" >&2
    exit 1
fi

# Parse arguments
PROJECT_NAME=""
FRAMEWORK=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --project-name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        --framework)
            FRAMEWORK="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: ./setup.sh --project-name PROJECT_NAME [--framework FRAMEWORK]"
            echo
            echo "Arguments:"
            echo "  --project-name    Name of your new project (required)"
            echo "  --framework       Optional framework (e.g., fastapi, react)"
            echo "  -h, --help        Show this help message"
            echo
            echo "Example:"
            echo "  ./setup.sh --project-name MyAwesomeProject --framework fastapi"
            exit 0
            ;;
        *)
            echo "${RED}[ERROR] Unknown argument: $1${RESET}" >&2
            echo "Run './setup.sh --help' for usage information" >&2
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$PROJECT_NAME" ]; then
    echo "${RED}[ERROR] --project-name is required${RESET}" >&2
    echo "Run './setup.sh --help' for usage information" >&2
    exit 1
fi

# Build Python command
PYTHON_ARGS="--project-name $PROJECT_NAME"
if [ -n "$FRAMEWORK" ]; then
    PYTHON_ARGS="$PYTHON_ARGS --framework $FRAMEWORK"
fi

# Execute setup.py
echo "${YELLOW}[INFO] Executing setup.py with arguments: $PYTHON_ARGS${RESET}"
echo

if ! $PYTHON_CMD setup.py $PYTHON_ARGS; then
    echo
    echo "${RED}[FAIL] Setup failed${RESET}" >&2
    exit 1
fi

echo
echo "${GREEN}[SUCCESS] Setup completed successfully${RESET}"
echo
echo "Next steps:"
echo "1. Review generated files"
echo "2. Edit .env with your configuration"
echo "3. Run: git add . && git commit -m \"feat: initial project setup\""
echo
