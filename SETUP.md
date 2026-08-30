# ProjetBiblio - Installation & Setup Guide

## Quick Start (Recommended)

### Option 1: Automatic (Recommended)
Simply run:
```
run.bat
```

This script will automatically:
- ✅ Detect/install Python 3.12 (if not found)
- ✅ Install all dependencies silently
- ✅ Start the API server
- ✅ Launch the terminal client

**Works on:** Any Windows PC with internet connection
**Time:** 2-5 minutes on first run

---

## Advanced Options

### Option 2: Bundle for Portability (Offline)
For maximum compatibility and offline usage:

```
bundle-setup.bat
```

This creates a local cache containing:
- Python installer
- All Python packages
- Configuration files

**Benefits:**
- ✅ Works on offline machines
- ✅ Faster installation on subsequent runs
- ✅ Portable to other PCs
- ✅ No repeated downloads

**Time:** 5-10 minutes first time (includes downloads)

After bundling, copy the entire project folder to other PCs and run `run.bat`.

---

### Option 3: Pre-flight Check
To verify system requirements:

```
preflight.bat
```

Checks:
- Windows version compatibility
- Internet connectivity
- Disk space
- Administrator privileges

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Windows | 7 SP1 | 10/11 |
| RAM | 2 GB | 4 GB+ |
| Disk Space | 1 GB free | 2 GB+ free |
| Internet | Required (first run only) | Recommended |
| Python | Auto-installed | Pre-installed |

---

## What Gets Installed

### Automatically Installed:
1. **Python 3.12** (~100 MB)
   - Windows package manager (winget) or direct download
   - Auto-added to PATH
   
2. **Dependencies** (from `requirements.txt`)
   - FastAPI (API server)
   - Pydantic (data validation)
   - python-dotenv (configuration)
   - And other required packages

3. **Database**
   - SQLite (local, no setup needed)
   - Or Turso (optional, if .env provided)

---

## How It Works

```
run.bat
  ├─> Find/Install Python
  ├─> Install Dependencies (pip)
  ├─> Start API Server (api.py)
  │   └─> Listens on http://localhost:8000
  ├─> Launch Terminal Client (main.py)
  │   └─> Connects to API via HTTP
  └─> Cleanup on Exit
```

### Architecture:
- **API Server**: Private (localhost only)
- **Terminal Client**: Public user interface
- **Database**: SQLite (local) or Turso (cloud)

---

## Troubleshooting

### Problem: "Python installation failed"
**Solution:**
1. Check internet connection
2. Disable antivirus temporarily
3. Run as Administrator
4. Check `%TEMP%\projetbiblio_setup.log`

### Problem: "Dependencies installation failed"
**Solution:**
1. Ensure internet connection is stable
2. Try running again (will retry automatically)
3. Check permissions on `%APPDATA%\pip`

### Problem: "API server won't start"
**Solution:**
1. Port 8000 may be in use: check with `netstat -ano | find "8000"`
2. Kill conflicting process: `taskkill /PID <PID> /F`
3. Check server log: `%TEMP%\projetbiblio_server.log`

### Problem: "Works on one PC, not another"
**Solution:**
1. Run `preflight.bat` to check system
2. Ensure Windows is fully updated
3. Install .NET Framework if missing
4. Try bundling with `bundle-setup.bat`

---

## Advanced: Manual Setup

If automatic setup fails:

```batch
REM 1. Install Python from python.org
REM    - Download from https://python.org/downloads
REM    - Run installer, check "Add Python to PATH"

REM 2. Install dependencies
py -m pip install -r requirements.txt

REM 3. Start server (in first terminal)
python api.py

REM 4. Run client (in second terminal)
python main.py
```

---

## Files Explained

| File | Purpose |
|------|---------|
| `run.bat` | Main launcher (use this!) |
| `bundle-setup.bat` | Create portable/offline bundle |
| `preflight.bat` | System requirements check |
| `api.py` | FastAPI server |
| `main.py` | Terminal client UI |
| `database.py` | Database connection (SQLite/Turso) |
| `requirements.txt` | Python dependencies |

---

## For Developers/Sharing

### Sharing with Friends:

**Option A: Send Entire Folder**
```
1. Run bundle-setup.bat (one time)
2. Zip entire project folder
3. Share with friends
4. They run run.bat
5. Everything works automatically!
```

**Option B: Just Share run.bat + Source**
```
1. Share project folder (without .projetbiblio-cache)
2. They run run.bat
3. Downloads and installs automatically
```

---

## Performance Optimization

### First Run (~3-5 minutes):
- Downloads Python (~100 MB)
- Downloads dependencies (~50-100 MB)
- Initial setup

### Subsequent Runs (~30 seconds):
- Just starts server and client
- No downloads needed

### Offline Mode:
- After running `bundle-setup.bat`
- Runs in seconds
- No internet required

---

## Security Notes

- ✅ No admin elevation required (installs per-user)
- ✅ Python installed to user folder
- ✅ Passwords never sent over network
- ✅ All downloads use HTTPS
- ✅ No telemetry or tracking

---

## Questions?

Check the main [README.md](README.md) for more information about ProjetBiblio itself.

For issues: Run `preflight.bat` and check `%TEMP%\projetbiblio_setup.log`
