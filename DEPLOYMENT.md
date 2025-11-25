# Deployment Guide - Moving to New System

## Quick Setup

The system now uses **dynamic path resolution** - it automatically finds the project files based on where the `.toe` file is located.

### Steps to Deploy

1. **Copy the entire `biotelia-td` folder** to the new machine
   - Can be anywhere: Desktop, Documents, different username, etc.
   - Keep all files together in the same folder structure

2. **Open `biotelia-pollination.toe`** in TouchDesigner
   - The system will automatically detect the correct path
   - No path editing required!

3. **Configure Production Settings** (in TouchDesigner UI)
   - Open `/project1/settings_control`
   - Set **Resolution Mode** → `Production 1920x2160`
   - Set **Input Source** → `Mocap/OSC`

4. **Done!**

## Path Resolution Logic

The system automatically tries these paths in order:

1. **TouchDesigner project folder** (`project.folder`)
   - Best option: detects where the .toe file is located
   - Works regardless of username or folder structure

2. **Fallback** (development only)
   - `/Users/unforced/Symbols/Codes/biotelia-td`
   - Only used if project.folder fails

## Troubleshooting Import Errors

### If you see "Cannot import 'core.system'" or similar:

**Check 1: Folder Structure**
```
biotelia-td/
├── biotelia-pollination.toe  ← Open this file
├── core/                      ← Must have these folders
│   ├── system.py
│   ├── agent.py
│   └── ...
├── config.py
└── ...
```

**Check 2: Python Path** (in TouchDesigner textport)
```python
>>> import sys
>>> print(sys.path[0])
```
Should show the biotelia-td folder location.

**Check 3: Verify project.folder**
```python
>>> print(project.folder)
```
Should show where the .toe file is located.

### Common Issues

**Issue:** "Module 'config' not found"
- **Cause:** Missing files or incorrect folder structure
- **Fix:** Ensure entire biotelia-td folder was copied, including all subfolders

**Issue:** "Path does not exist: /Users/unforced/..."
- **Cause:** Old hardcoded path (shouldn't happen with new version)
- **Fix:** Make sure you're using the latest committed version

**Issue:** "Cannot import 'numpy'" or other packages
- **Cause:** TouchDesigner's Python missing dependencies
- **Fix:** Install required packages in TouchDesigner's Python:
  ```bash
  # In terminal (macOS):
  /Applications/TouchDesigner.app/Contents/Frameworks/Python.framework/Versions/Current/bin/pip3 install numpy
  ```

## File Locations on New Machine

The files can be located **anywhere** - just keep them together:

✅ `/Users/newuser/Desktop/biotelia-td/` (Different user)
✅ `/Users/jane/Documents/Projects/biotelia-td/` (Different path)
✅ `C:/Users/Jane/biotelia-td/` (Windows, if needed)
✅ `/home/user/biotelia-td/` (Linux, if needed)

## Verifying Successful Setup

After opening the .toe file, check the textport for:
```
✓ Biotelia Pollination System initialized (TEST/PRODUCTION mode)
  - Canvas: [width]x[height]
  - Structures: 3
  - Agents: 3 (bee, butterfly, moth)
  - Settings: TouchDesigner UI (/project1/settings_control)
```

If you see this, the paths are working correctly!

## Production Checklist

- [ ] Copy entire biotelia-td folder to new machine
- [ ] Open biotelia-pollination.toe in TouchDesigner
- [ ] Verify no import errors in textport
- [ ] Open `/project1/settings_control`
- [ ] Set Resolution Mode → Production 1920x2160
- [ ] Set Input Source → Mocap/OSC
- [ ] Configure mocap system to send to port 9000
- [ ] Test with mocap input
- [ ] Verify rendering output looks correct

## Need Help?

If you still see path errors:
1. Check that all files copied correctly
2. Verify folder structure is intact (core/, docs/, etc.)
3. Try opening textport and running:
   ```python
   >>> import sys, os
   >>> print("Project folder:", project.folder)
   >>> print("Path exists:", os.path.exists(project.folder))
   ```

The system should work out-of-the-box on any machine with TouchDesigner installed!
