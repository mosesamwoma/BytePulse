# Installation Guide

## Quick Copy-Paste (3 steps)

### Step 1: Create setup folder

```powershell
mkdir setup
```

### Step 2: Copy files into `setup/` folder

These 3 files go into: `BytePulse/setup/`

- `README.md` (this file)
- `setup_bytepulse.py`
- `setup_bytepulse.bat`

### Step 3: Copy launcher to root

This file goes into: `BytePulse/` (root, not setup/)

- `launch_bytepulse.bat`

---

## Final Structure

After copying, your folder should look like:

```
BytePulse/
├── setup/
│   ├── README.md
│   ├── INSTALL.md (this file)
│   ├── setup_bytepulse.py
│   └── setup_bytepulse.bat
├── launch_bytepulse.bat
├── src/
├── app.py
├── requirements.txt
└── ... (other files)
```

---

## Run Setup

### Option A: Python

```powershell
python setup/setup_bytepulse.py
```

### Option B: Batch (Double-click)

```
setup\setup_bytepulse.bat
```

### Option C: PowerShell (As Administrator)

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
python setup/setup_bytepulse.py
```

---

## What Happens Next

1. Setup auto-elevates to Administrator
2. Installs all dependencies
3. Creates data/ and logs/ folders
4. Initializes SQLite database
5. Registers Task Scheduler tasks
6. Creates launcher shortcut
7. Asks to launch BytePulse

**Then:**
- Click Yes on UAC prompt (if appears)
- Wait 1-2 minutes for dependencies
- Restart your PC
- BytePulse starts automatically

---

## Verify Installation

### Check Python

```powershell
python --version
```

Should show: `Python 3.11.x`

### Check tasks registered

```powershell
Get-ScheduledTask -TaskName "BytePulse-Tray"
Get-ScheduledTask -TaskName "BytePulse-Tracker"
```

Both should show `State: Ready`

### Check files created

```powershell
ls data/
ls logs/
```

Both folders should exist.

### Check database

```powershell
sqlite3 data/bytepulse.db ".tables"
```

Should show table: `sessions`

---

## Troubleshooting

### "Python not found"

1. Download Python 3.11 from [python.org](https://www.python.org/downloads/)
2. Check **"Add Python to PATH"** during install
3. Run setup again

### Setup needs admin

This is normal. Click **Yes** on the UAC prompt.

### Tasks not registering

1. Right-click setup script
2. Select "Run as Administrator"
3. Run setup again

### No tray icon after restart

1. Check if you actually restarted (not just logged out)
2. Look for hidden icons in system tray (click `^` arrow)
3. Check `data/tracker.log` for errors

---

## Next Steps

After setup completes:

1. **Manual launch** (anytime):
   ```
   Double-click: launch_bytepulse.bat
   ```

2. **View dashboard**:
   ```
   http://localhost:8501
   ```

3. **Check status**:
   - Right-click system tray icon
   - Select "Status"

4. **Read full README**:
   - See: `setup/README.md`

---

## Need Help?

1. Check `data/tracker.log` for errors
2. Read full README in `setup/README.md`
3. Open issue on GitHub: [github.com/mosesamwoma/BytePulse](https://github.com/mosesamwoma/BytePulse)

---

<div align="center">
<strong>Setup complete? Restart your PC to start BytePulse automatically.</strong>
</div>
