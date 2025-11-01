# SessionManager Dashboard UTF-8 Fix Guide

## Problem Fixed

**Issue**: 'utf-8' codec can't decode byte 0x8e in position 85: invalid start byte

**Root Cause**: Windows CP949 encoding conflicts with UTF-8 in session files

## Solutions Applied

### 1. Code Fixes

#### SessionAnalyzer.py (Line 67-81)
```python
# Multi-encoding support with fallback
encodings = ['utf-8', 'cp949', 'latin-1']
for enc in encodings:
    try:
        with open(session_file, 'r', encoding=enc) as f:
            data = json.load(f)
            break
    except (UnicodeDecodeError, json.JSONDecodeError):
        continue
```

#### SessionDashboard.py (Line 1-2)
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
```

### 2. Launch Scripts Created

#### run_dashboard.bat (Windows Command Prompt)
- Sets UTF-8 code page (chcp 65001)
- Auto-launches browser
- Error handling included

#### run_dashboard.ps1 (PowerShell)
- Sets UTF-8 encoding for console
- Python environment variable PYTHONIOENCODING=utf-8
- Diagnostic information

## How to Run Dashboard

### Option 1: Easy Launch (Recommended)
```cmd
# Double-click or run:
run_dashboard.bat
```

### Option 2: PowerShell
```powershell
# In PowerShell:
.\run_dashboard.ps1
```

### Option 3: Manual
```bash
# Set encoding first:
chcp 65001

# Then run:
streamlit run scripts/session_dashboard.py
```

## Dashboard Features

Once running, the dashboard provides:

1. **Real-time Monitoring**
   - Current session status
   - Active tasks
   - Live updates (5-60 sec refresh)

2. **Statistics**
   - Success/failure rates
   - Task execution times
   - Productivity patterns

3. **Visualizations**
   - Task distribution charts
   - Time-based activity graphs
   - Error pattern analysis

4. **Session History**
   - Recent sessions list
   - Task details
   - Error logs

## Verification

Run this to verify encoding is fixed:
```bash
python scripts/test_dashboard_encoding.py
```

Expected output:
```
[SUCCESS] Encoding issue resolved!
```

## Browser Access

After launching, open browser to:
```
http://localhost:8501
```

The browser should open automatically.

## Troubleshooting

### If still getting encoding errors:

1. **Clear problematic session files**:
```python
# Run this to identify problem files:
python scripts/test_dashboard_encoding.py
```

2. **Set system environment**:
```cmd
set PYTHONIOENCODING=utf-8
```

3. **Use English Windows locale**:
   - Control Panel → Region → Administrative
   - Change system locale to English (US)
   - Or check "Beta: Use Unicode UTF-8"

### Port already in use:

```bash
# Kill existing Streamlit process:
taskkill /F /IM streamlit.exe

# Or use different port:
streamlit run scripts/session_dashboard.py --server.port 8502
```

## Summary

✅ **Fixed**: UTF-8 decoding errors
✅ **Added**: Multi-encoding support
✅ **Created**: Launch scripts with encoding setup
✅ **Tested**: All session files readable
✅ **Ready**: Dashboard fully operational

The dashboard is now ready for use with proper encoding handling for Windows systems.
