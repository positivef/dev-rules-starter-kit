# SessionManager Dashboard UTF-8 Encoding Fix - Complete Guide

## Problem Summary

**Error**: `'utf-8' codec can't decode byte 0x8e in position 85: invalid start byte`

**Impact**: Dashboard fails to load with Script execution error

## Root Causes Identified

1. **JSON Files**: Using `ensure_ascii=False` in Windows environment
2. **Python Comments**: Korean characters in source files
3. **Environment Variables**: Missing PYTHONIOENCODING setting
4. **Streamlit**: Internal handling of non-ASCII data

## Complete Solution Applied

### 1. Code Fixes

#### A. SessionManager.py (Line 204)
```python
# Before:
json.dump(self.current_state.to_dict(), f, indent=2, ensure_ascii=False)

# After:
json.dump(self.current_state.to_dict(), f, indent=2, ensure_ascii=True)
```

#### B. SessionAnalyzer.py
- Added multi-encoding support (UTF-8, CP949, Latin-1)
- Changed JSON output to `ensure_ascii=True`

#### C. SessionReportGenerator.py
- Changed to `ensure_ascii=True` for all JSON outputs

### 2. Session Cleanup

Created `clean_and_restart_sessions.py` to:
- Backup all existing session files
- Remove problematic sessions
- Start fresh with ASCII-safe data

### 3. Environment Setup

Created enhanced launchers with proper UTF-8 configuration:

#### run_dashboard_fixed.bat
```batch
@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
python -X utf8 -m streamlit run scripts/session_dashboard.py
```

## How to Use the Fixed Dashboard

### Method 1: Clean Start (Recommended)
```bash
# 1. Clean all sessions
python scripts/clean_and_restart_sessions.py

# 2. Run with fixed launcher
run_dashboard_fixed.bat
```

### Method 2: Manual Environment Setup
```bash
# Set environment variables
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
chcp 65001

# Run with UTF-8 mode
python -X utf8 -m streamlit run scripts/session_dashboard.py
```

### Method 3: Python Script
```bash
python scripts/test_dashboard_with_env.py
```

## Files Modified

| File | Changes | Impact |
|------|---------|--------|
| session_manager.py | ensure_ascii=True | Safe JSON encoding |
| session_analyzer.py | Multi-encoding support + ensure_ascii=True | Handle legacy files |
| session_report_generator.py | ensure_ascii=True | Safe report generation |
| session_dashboard.py | UTF-8 declaration | Proper encoding |

## Scripts Created

1. **fix_session_encoding.py** - Detect and fix encoding issues
2. **find_problematic_session.py** - Locate files with byte 0x8e
3. **clean_and_restart_sessions.py** - Clean slate approach
4. **find_byte_in_python_files.py** - Source code analysis
5. **test_dashboard_with_env.py** - Test with proper environment
6. **run_dashboard_fixed.bat** - Production launcher

## Verification Steps

### 1. Check Sessions
```bash
python scripts/find_problematic_session.py
```
Expected: "No problematic files found"

### 2. Test Dashboard
```bash
python test_dashboard_webapp.py
```
Expected: No encoding errors

### 3. Manual Check
1. Open http://localhost:8501
2. No "Script execution error" should appear
3. Dashboard loads normally

## Prevention Measures

### For Developers

1. **Always use ASCII-safe JSON**:
```python
json.dump(data, f, indent=2, ensure_ascii=True)
```

2. **Set environment in development**:
```bash
set PYTHONIOENCODING=utf-8
```

3. **Use English comments in critical files**

4. **Test on Windows regularly**

### For Production

1. Use `run_dashboard_fixed.bat` for launching
2. Set system environment variables permanently
3. Regular session cleanup (monthly)

## Troubleshooting

### If errors persist:

1. **Clear all caches**:
```bash
rmdir /s /q .streamlit
rmdir /s /q __pycache__
```

2. **Check Python version**:
```bash
python --version  # Should be 3.8+
```

3. **Reinstall Streamlit**:
```bash
pip uninstall streamlit
pip install streamlit --no-cache-dir
```

4. **Windows locale settings**:
- Control Panel → Region → Administrative
- Change system locale → Check "Beta: Use Unicode UTF-8"

## Technical Details

### Why byte 0x8e at position 85?

- Windows CP949 encoding uses 0x8e for certain Korean characters
- Position 85 often falls in timestamp or metadata fields
- JSON serialization without ensure_ascii preserves raw bytes

### Why ensure_ascii=True fixes it?

- Converts all non-ASCII to Unicode escape sequences
- Example: "한글" → "\ud55c\uae00"
- Always safe for JSON parsing regardless of system encoding

## Testing Results

✅ **Session files**: Clean and UTF-8 compliant
✅ **Dashboard loading**: No encoding errors
✅ **Data persistence**: Working correctly
✅ **Report generation**: All formats working
✅ **Cross-platform**: Windows/Linux compatible

## Conclusion

The encoding issue is fully resolved through:
1. Code changes to enforce ASCII-safe JSON
2. Proper environment configuration
3. Clean session restart
4. Enhanced launchers with UTF-8 settings

The dashboard now runs reliably on Windows systems without encoding errors.

---

**Version**: 1.0.0
**Last Updated**: 2025-10-27
**Status**: ✅ FIXED
