# Development Assistant - Configuration Quick Reference

## pyproject.toml Configuration

```toml
[tool.dev-assistant]
# Enable/disable the assistant
enabled = true

# Directories to watch for Python file changes
# Default: ["scripts", "tests"]
watch_paths = ["scripts", "tests"]

# Debounce time in milliseconds (avoid redundant processing)
# Default: 500
# Recommended: 200-1000
debounce_ms = 500

# Ruff verification timeout in seconds
# Default: 2.0
# Recommended: 1.0-5.0
verification_timeout_sec = 2.0

# Evidence log retention in days
# Default: 7
# Recommended: 3-30
log_retention_days = 7

# Enable Ruff code verification
# Default: true
enable_ruff = true

# Enable automatic evidence logging
# Default: true
enable_evidence = true
```

## CLI Arguments

| Argument | Type | Description | Example |
|----------|------|-------------|---------|
| `--watch-dirs` | list | Override watch paths | `--watch-dirs scripts tests src` |
| `--debounce` | int | Override debounce time (ms) | `--debounce 1000` |
| `--log-level` | choice | Set logging level | `--log-level DEBUG` |
| `--no-ruff` | flag | Disable Ruff verification | `--no-ruff` |
| `--no-evidence` | flag | Disable evidence logging | `--no-evidence` |

## Configuration Priority

1. **CLI Arguments** (highest priority)
2. **pyproject.toml** [tool.dev-assistant]
3. **Default Values** (lowest priority)

CLI arguments override configuration file values.

## Common Configurations

### Minimal Setup (No Config File)
```bash
python scripts/dev_assistant.py
# Uses all defaults
```

### Custom Directories
```toml
[tool.dev-assistant]
watch_paths = ["src", "lib", "app", "tests"]
```

### High-Performance Setup
```toml
[tool.dev-assistant]
debounce_ms = 200
verification_timeout_sec = 1.0
```

### Minimal Logging
```toml
[tool.dev-assistant]
log_retention_days = 3
enable_evidence = false
```

### Development Mode
```bash
python scripts/dev_assistant.py --log-level DEBUG --debounce 100
```

### CI/CD Mode
```bash
python scripts/dev_assistant.py --no-evidence --log-level WARNING
```

## Validation Rules

| Parameter | Type | Constraints |
|-----------|------|-------------|
| `enabled` | bool | Must be true or false |
| `watch_paths` | list[str] | Non-empty, strings only |
| `debounce_ms` | int | >= 0 |
| `verification_timeout_sec` | float | > 0 |
| `log_retention_days` | int | >= 0 |
| `enable_ruff` | bool | Must be true or false |
| `enable_evidence` | bool | Must be true or false |

Invalid configurations raise `RuntimeError` with detailed error messages.

## Examples

### Example 1: Basic Usage
```bash
# Create pyproject.toml with defaults
cat > pyproject.toml << EOF
[tool.dev-assistant]
enabled = true
watch_paths = ["scripts", "tests"]
EOF

# Run with config
python scripts/dev_assistant.py
```

### Example 2: Temporary Override
```bash
# Use config but override specific settings
python scripts/dev_assistant.py --watch-dirs src --debounce 1000
```

### Example 3: Disable Temporarily
```bash
# Run without Ruff or evidence logging
python scripts/dev_assistant.py --no-ruff --no-evidence
```

### Example 4: Custom Project Structure
```toml
[tool.dev-assistant]
watch_paths = ["backend/src", "backend/tests", "shared/utils"]
debounce_ms = 300
log_retention_days = 14
```

## Troubleshooting

### "tomllib/tomli not available" Warning
```bash
# Python 3.11+: stdlib support (no action needed)
# Python 3.8-3.10: Install tomli
pip install tomli
```

### "Invalid configuration" Error
- Check TOML syntax (use TOML validator)
- Verify parameter types match requirements
- Review validation constraints table

### Configuration Not Loading
- Verify `pyproject.toml` exists in project root
- Check file is valid TOML format
- Run with `--log-level DEBUG` to see config loading messages

### CLI Override Not Working
- Ensure argument syntax is correct
- Check `--help` for available options
- CLI arguments must match expected types

## Dependencies

Required:
- `watchdog>=3.0.0` (file watching)
- `ruff>=0.1.0` (code verification)

Optional:
- `tomli>=2.0.0` (Python <3.11 only, for config support)

## Best Practices

1. **Start with defaults**: Run without config first
2. **Iterate gradually**: Add config options as needed
3. **Use CLI for testing**: Test settings before adding to config
4. **Document custom configs**: Add comments in pyproject.toml
5. **Version control**: Commit pyproject.toml with project
6. **Monitor evidence**: Review logs to tune retention days
7. **Adjust debounce**: Higher for slow systems, lower for fast

## Support

- Documentation: `README.md` - Development Assistant section
- Help text: `python scripts/dev_assistant.py --help`
- Tests: `pytest tests/test_dev_assistant.py -k Config`
- Issues: Check validation error messages for details
