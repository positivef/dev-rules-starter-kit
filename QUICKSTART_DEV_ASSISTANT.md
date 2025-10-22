# Development Assistant - Quick Start Guide

**Status**: Production Ready (Phase A Complete)
**Version**: 1.0.0
**Date**: 2025-10-22

## 30-Second Start

```bash
# 1. Install dependency (if not already)
pip install watchdog>=3.0.0

# 2. Run the watcher
python scripts/dev_assistant.py

# 3. Edit any .py file in scripts/ or tests/
# 4. Watch console for [MODIFIED] events
# 5. Press Ctrl+C to stop
```

## What You Get

When you run the watcher, it will:

1. **Monitor** all Python files in `scripts/` and `tests/`
2. **Detect** changes within 500ms (debounced)
3. **Log** each change to console with timestamp
4. **Run quietly** at <2% CPU when idle
5. **Shutdown cleanly** on Ctrl+C

## Example Output

```
============================================================
Development Assistant - File Watcher
============================================================
Watching: scripts/
Watching: tests/
Debounce time: 500ms
File watcher active. Press Ctrl+C to stop.

08:15:42 | INFO    | [MODIFIED] scripts/dev_assistant.py
08:15:45 | INFO    | [MODIFIED] tests/test_dev_assistant.py
08:15:48 | INFO    | [CREATED] scripts/new_feature.py
^C
Shutdown signal received. Stopping gracefully...
Development Assistant stopped cleanly.
```

## Common Use Cases

### Watch Different Directories
```bash
python scripts/dev_assistant.py --watch-dirs src lib tests
```

### Faster Response (100ms debounce)
```bash
python scripts/dev_assistant.py --debounce 100
```

### Debug Mode (see all events)
```bash
python scripts/dev_assistant.py --log-level DEBUG
```

## Testing It Works

### Method 1: Manual Test Script
```bash
# Terminal 1: Run watcher
python scripts/dev_assistant.py

# Terminal 2: Trigger events
python scripts/test_watcher_manual.py
```

### Method 2: Quick Edit
```bash
# Terminal 1: Run watcher
python scripts/dev_assistant.py

# Terminal 2: Touch a file
echo "# test" >> scripts/temp_test.py
# Should see [CREATED] event

# Edit it
echo "# modified" >> scripts/temp_test.py
# Should see [MODIFIED] event

# Clean up
rm scripts/temp_test.py
```

### Method 3: Run Tests
```bash
# Verify everything works
python -m pytest tests/test_dev_assistant.py -v

# Should see: 22 passed
```

## Troubleshooting

**Problem**: "No valid directories to watch"
**Solution**: Make sure `scripts/` and `tests/` exist in your current directory

**Problem**: No events showing up
**Solution**: Only `.py` files are monitored. Try editing a Python file.

**Problem**: Too many events
**Solution**: Increase debounce time: `--debounce 1000`

## Next Steps

This is **Phase A** - basic file watching with logging.

**Coming in Phase B**:
- Automatic linting when you save
- Run relevant tests automatically
- Pre-commit hook integration

**Want to contribute?**
See `claudedocs/dev_assistant_implementation.md` for architecture details.

## Files Reference

- **Main script**: `scripts/dev_assistant.py`
- **Tests**: `tests/test_dev_assistant.py`
- **Manual test**: `scripts/test_watcher_manual.py`
- **Documentation**: `scripts/README_DEV_ASSISTANT.md`
- **Technical report**: `claudedocs/dev_assistant_implementation.md`

## Help & Support

```bash
# Show all options
python scripts/dev_assistant.py --help
```

**Questions?** Check the README: `scripts/README_DEV_ASSISTANT.md`

---

**Happy coding!** The watcher is here to help streamline your development workflow.
