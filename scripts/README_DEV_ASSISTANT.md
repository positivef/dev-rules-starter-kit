# Development Assistant - File Watcher

Production-ready file watcher that monitors Python files and logs changes in real-time.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run watcher (watches scripts/ and tests/ by default)
python scripts/dev_assistant.py
```

Press `Ctrl+C` to stop cleanly.

## Features

- ✅ Monitors Python files in `scripts/` and `tests/` directories
- ✅ Debounces file changes (500ms default) to avoid redundant processing
- ✅ Runs in background with <2% CPU when idle
- ✅ Graceful shutdown on Ctrl+C
- ✅ Thread-safe queue-based processing
- ✅ Clean console output with timestamps

## Usage

### Basic

```bash
# Default behavior
python scripts/dev_assistant.py
```

### Custom Directories

```bash
# Watch custom directories
python scripts/dev_assistant.py --watch-dirs scripts tests custom_dir
```

### Adjust Debounce Time

```bash
# 1 second debounce
python scripts/dev_assistant.py --debounce 1000

# 100ms debounce (faster response)
python scripts/dev_assistant.py --debounce 100
```

### Debug Mode

```bash
# Show all events including filtered ones
python scripts/dev_assistant.py --log-level DEBUG
```

## Testing

```bash
# Run unit tests
python -m pytest tests/test_dev_assistant.py -v

# Run with coverage
python -m pytest tests/test_dev_assistant.py --cov=scripts.dev_assistant

# Manual interactive test
python scripts/test_watcher_manual.py
```

## Architecture

```
DevAssistant
├── FileChangeDebouncer (500ms debouncing)
├── PythonFileHandler (filters .py files)
├── FileChangeProcessor (background processing)
└── Observer (watchdog file watcher)
```

**Thread Model**:
- Main thread: Signal handling + keep-alive
- Observer thread: File system monitoring
- Processor thread: Event processing from queue

## Configuration

Current configuration via CLI arguments only. Future versions will support `pyproject.toml`.

## Performance

- **CPU Usage**: <2% when idle
- **Processing**: ~830 events/second
- **Memory**: ~22MB stable footprint
- **Debouncing**: Thread-safe, no race conditions

## Error Handling

- Invalid directories → Runtime error at startup
- Processing errors → Logged but watcher continues
- Graceful shutdown → 5-second timeout for cleanup

## Future Enhancements

Phase A (Current): File watching + logging
Phase B (Next): Linting + testing integration
Phase C: Configuration system (pyproject.toml)
Phase D: Advanced features (batch processing, diff analysis)
Phase E: Monitoring & analytics

## Troubleshooting

**Watcher doesn't start**:
- Check directories exist: `ls scripts tests`
- Verify permissions: Should be readable

**High CPU usage**:
- Check for file modification loops
- Increase debounce time: `--debounce 1000`

**Events not detected**:
- Verify watching correct directories
- Check file extension is `.py`
- Try DEBUG mode: `--log-level DEBUG`

## License

Part of dev-rules-starter-kit project.
