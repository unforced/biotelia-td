# TouchDesigner File Verification Guide

**File:** `biotelia-pollination.toe` (root directory)
**Created:** 2025-11-25

## When to Use This Guide

Use this checklist whenever:
- Opening the TD file for the first time
- After moving the project to a new location
- After updating Python code
- Troubleshooting rendering issues

---

## Pre-Flight Checklist

### 1. Verify Python Path

**Location:** `/project1/python_path` (Text DAT)

**Should contain:**
```
/Users/unforced/Symbols/Codes/biotelia-td
```

**How to fix if wrong:**
1. Click on the `python_path` Text DAT
2. Update the path to point to this project directory
3. The path should be the absolute path to `biotelia-td/`

### 2. Check Python Import

**Location:** `/project1/setup_python_path` (Execute DAT)

**Should run automatically** on file open and add the path to `sys.path`

**To verify:**
1. Open Textport (Alt+T)
2. Type: `import sys; print('\n'.join(sys.path))`
3. Verify the biotelia-td path is in the list

**If imports fail:**
1. Check that `python_path` Text DAT has correct path
2. Manually run: `op('/project1/setup_python_path').run()`

### 3. Verify System Initialization

**Location:** `/project1/pollination_system` (Python DAT)

**To verify:**
1. Look at the Textport for "✓ Biotelia Pollination System initialized"
2. Or manually run: `op('/project1/pollination_system').module.initialize()`

**Common issues:**
- ImportError: Check python_path is correct
- Missing modules: Run `pip install -r requirements.txt` in terminal

---

## Testing the Render Output

### 4. Check Primary Output

**Location:** `/project1/gpu_renderer/OUT` (Script TOP)

**Should show:**
- Dark green background
- 5 colored structures (trees)
- 3 moving autonomous agents (bee, butterfly, moth)
- Mycelial network connections
- Mouse cursor when over TD window
- Trails when mouse moves near structures

### 5. Test Mouse Interaction

**How to test:**
1. Move mouse over the TouchDesigner window
2. You should see a colored dot following your cursor
3. Move near a colored tree (within ~80 pixels)
4. Your cursor should absorb the tree's color
5. Moving should leave a colored trail that fades

### 6. Verify Data Tables

**Locations:** `/project1/*_data` (Table DATs)

**Check these tables have data:**

| Table | Expected Rows | What It Contains |
|-------|--------------|------------------|
| `structures_data` | 6 (header + 5 trees) | Tree positions and colors |
| `visitors_data` | Variable (1-10) | Visitors + autonomous agents |
| `trails_data` | Variable (0-500) | Trail particle points |
| `particles_data` | Variable (0-100) | Spiral pollination effects |

**How to check:**
- Click on each `*_data` Table DAT
- Bottom panel shows the table contents
- Should have columns: `id, tx, ty, r, g, b, radius, alpha`

### 7. Verify Timer is Running

**Location:** `/project1/frame_timer` (Timer CHOP)

**Should be:**
- Playing (not paused)
- Cycling continuously
- Rate: 1 (for 60 FPS)

**To verify:**
- Look at the Timer CHOP
- The value should be cycling from 0 to 1
- If stopped, click the "Initialize" parameter or press "Play"

---

## Performance Checks

### 8. Measure Cook Times

**In Textport (Alt+T), run:**
```python
# Check renderer performance
renderer = op('/project1/gpu_renderer/optimized_circles')
print(f"Renderer cook time: {renderer.cookTime:.2f}ms")

# Check system update performance
system = op('/project1/pollination_system')
print(f"System cook time: {system.cookTime:.2f}ms")
```

**Expected values:**
- Renderer: < 2ms (for full scene with ~100-200 particles)
- System: < 1ms

**If cook times are high:**
- Check if you have other heavy operators running
- Verify frame timer is at correct rate (60 FPS)
- Check for Python errors in Textport

### 9. Check Frame Rate

**In TD:**
- Look at the title bar (shows FPS)
- Should be close to 60 FPS

**If low FPS:**
- Check cook times (step 8)
- Reduce trail length in `config.py` (`TRAIL_MAX_POINTS`)
- Check system resources (CPU/memory)

---

## Troubleshooting Common Issues

### Issue: Blank/Black Output

**Possible causes:**
1. Python system not initialized
   - **Fix:** Run `op('/project1/pollination_system').module.initialize()`
2. Timer not running
   - **Fix:** Start the `frame_timer` Timer CHOP
3. Renderer not cooking
   - **Fix:** Check for errors in Textport

### Issue: No Moving Agents

**Possible causes:**
1. Timer not triggering updates
   - **Fix:** Verify `frame_timer` is running and connected
2. Data not being exported
   - **Fix:** Check `hybrid_data_exporter` for errors

### Issue: Import Errors

**Error message:** `ImportError: No module named 'core'`

**Fixes:**
1. Verify `python_path` Text DAT has correct path
2. Run `op('/project1/setup_python_path').run()`
3. In terminal: `cd /Users/unforced/Symbols/Codes/biotelia-td && pip install -r requirements.txt`

### Issue: Old Path References

**Error message:** Path contains `biotelia-viz` or other old location

**Fixes:**
1. Update `python_path` Text DAT to current location
2. Search network for hardcoded paths (unlikely but possible)
3. May need to re-create setup_python_path Execute DAT

---

## Network Organization

The TD file should have this structure:

```
/project1/
├── Input (X: 0)
│   ├── mouse_input
│   └── scale_to_canvas
│
├── Python Logic (X: 300)
│   ├── python_path
│   ├── setup_python_path
│   ├── pollination_system
│   ├── frame_timer
│   ├── frame_timer_callbacks1
│   └── hybrid_data_exporter
│
├── Data Tables (X: 600)
│   ├── structures_data
│   ├── visitors_data
│   ├── trails_data
│   └── particles_data
│
└── Renderers (X: 900)
    ├── gpu_renderer ⭐ (optimized)
    └── hybrid_render (old/backup)
```

For more details, see [NETWORK_LAYOUT.md](NETWORK_LAYOUT.md)

---

## Quick Test Script

**Run this in Textport to test everything:**

```python
# Quick verification script
print("=" * 50)
print("BIOTELIA TD VERIFICATION")
print("=" * 50)

# 1. Check path
path_dat = op('/project1/python_path')
if path_dat:
    print(f"✓ Python path: {path_dat.text}")
else:
    print("✗ python_path DAT not found!")

# 2. Check system
poll_sys = op('/project1/pollination_system')
if poll_sys:
    print(f"✓ Pollination system DAT exists")
    try:
        system = poll_sys.module._system
        if system:
            print(f"✓ System initialized")
        else:
            print("⚠ System not initialized - run initialize()")
    except:
        print("⚠ System module not loaded")
else:
    print("✗ pollination_system DAT not found!")

# 3. Check renderer
renderer = op('/project1/gpu_renderer/OUT')
if renderer:
    print(f"✓ Renderer exists (cook time: {renderer.cookTime:.2f}ms)")
else:
    print("✗ gpu_renderer/OUT not found!")

# 4. Check data tables
tables = ['structures_data', 'visitors_data', 'trails_data', 'particles_data']
for table_name in tables:
    table = op(f'/project1/{table_name}')
    if table:
        rows = table.numRows - 1  # Minus header
        print(f"✓ {table_name}: {rows} rows")
    else:
        print(f"✗ {table_name} not found!")

# 5. Check timer
timer = op('/project1/frame_timer')
if timer:
    is_playing = timer.par.play.eval()
    print(f"✓ Timer: {'Playing' if is_playing else '⚠ STOPPED'}")
else:
    print("✗ frame_timer not found!")

print("=" * 50)
print("Verification complete!")
print("=" * 50)
```

---

## Success Criteria

✅ **Everything is working if:**

1. No errors in Textport
2. `/project1/gpu_renderer/OUT` shows the scene
3. Mouse interaction works (cursor absorbs tree colors)
4. 3 autonomous agents are moving
5. Data tables are populated
6. Cook times are < 2ms
7. Running at ~60 FPS

---

## Next Steps After Verification

Once verified:
1. Test with real mocap data (see [MOCAP_SETUP.md](MOCAP_SETUP.md))
2. Calibrate projector mapping
3. Adjust colors/parameters in `config.py`
4. Add more autonomous agents if desired

---

**Reference Files:**
- [NETWORK_LAYOUT.md](NETWORK_LAYOUT.md) - Full network structure
- [HYBRID_APPROACH.md](HYBRID_APPROACH.md) - Architecture explanation
- [OPTIMIZED_RENDERING.md](OPTIMIZED_RENDERING.md) - Performance details
- [MOCAP_SETUP.md](MOCAP_SETUP.md) - Motion capture integration
