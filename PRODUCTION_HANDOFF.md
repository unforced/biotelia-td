# Biotelia Pollination System - Production Handoff

**Last Updated:** 2025-11-25
**Status:** ✅ Production Ready - Mocap Mode
**Resolution:** 1920 × 2160 (portrait 8:9 aspect)

---

## Quick Start

### On Production Machine

1. **Clone the repository:**
   ```bash
   git clone https://github.com/unforced/biotelia-td.git
   cd biotelia-td
   ```

2. **Open TouchDesigner file:**
   - Open `biotelia-pollination.toe`
   - System will automatically find project files (dynamic path resolution)

3. **Configure for production:**
   - Open `/project1/settings_control`
   - Set **Resmode** → `Production 1920x2160`
   - Set **Inputmode** → `Mocap/OSC`

4. **Configure mocap coordinate mapping:**
   - Open `/project1/mocap`
   - Go to **"Coordinate Mapping"** parameters
   - Current settings are pre-configured for:
     - Room: 20 ft × 30 ft
     - Projection: 7 ft × 8 ft (centered)
     - Mocap range: -1 to 1

5. **Verify mocap input:**
   - Check `/project1/mocap/oscin1` is receiving on port **55556**
   - Channels should appear as: p0x, p0y, p0z, p1x, p1y, p1z, etc.

6. **Check output:**
   - View `/project1/gpu_renderer/OUT`
   - Should show 1920×2160 rendering with mocap-tracked visitors

---

## System Overview

### What It Does

Interactive floor projection where visitors become pollinators:
- **Touch a structure** (tree) → Absorb its glowing color into your aura
- **Move through space** → Leave colored trails that fade over time
- **Touch different structure** → Create spiral pollination dance effect
- **Autonomous agents** → None in production mode (mocap-only)

### Current Configuration

**Canvas:** 1920 × 2160 pixels (portrait)
**Input:** Mocap/OSC on port 55556
**Visitors:** Up to 9 tracked simultaneously
**Autonomous agents:** Disabled in mocap mode
**Structures:** 3 colored trees at fixed positions

---

## TouchDesigner Network Structure

### Essential Nodes (14 total)

**Input & Settings Row:**
- `settings_control` - UI controls for Resolution/Input mode
- `mocap` - Mocap COMP with coordinate mapping
- `input_switch` - Switches between mocap/test inputs
- `input_selector` - Selects active input

**Core System Row:**
- `pollination_system` - Python logic (DAT)
- `gpu_renderer` - Rendering output (COMP)

**Timing Row:**
- `frame_timer` - Animation timing
- `frame_timer_callbacks1` - Timer callbacks
- `frame_speed` - Frame rate control
- `animation_driver` - Noise-based animation
- `update_pulse` - Update trigger

**Utilities Row:**
- `mcp_webserver_base` - MCP server for remote control
- `python_path` - Project path setup
- `setup_python_path` - Path initialization

---

## Mocap Coordinate Mapping

### Current Configuration

The system is pre-configured for your specific room:

**Room Dimensions:**
- 20 ft wide × 30 ft long

**Projection Area:**
- 7 ft wide × 8 ft long
- Centered in room

**Mocap Range:**
- -1 to 1 (center of room = 0, 0)

**Mapping Parameters:**
- X Scale: **2742.86**
- X Offset: **960**
- Y Scale: **4050**
- Y Offset: **1080**
- Input Range: **neg1to1**

### How It Works

- Person at room center (0, 0) → Canvas center (960, 1080)
- Projection edges map exactly to canvas edges (0, 0) to (1920, 2160)
- People outside the 7×8 ft area will be off-canvas

### To Adjust in Production

If the mapping needs tuning:

1. Open `/project1/mocap`
2. Go to **"Coordinate Mapping"** page
3. Adjust parameters:
   - **X/Y Scale** - How much to multiply coordinates
   - **X/Y Offset** - How much to shift coordinates
   - **Input Range** - Toggle between 0-1 or -1 to 1

**Formula:** `canvas_position = (mocap_value × Scale) + Offset`

---

## Settings & Configuration

### Resolution Settings

Located at: `/project1/settings_control`

**Resmode options:**
- `Test 1138x1280` - For testing without commercial license
- `Production 1920x2160` - **Use this for production**

**Inputmode options:**
- `Mouse/Test` - For development/testing
- `Mocap/OSC` - **Use this for production**

### Python Configuration

File: `config.py`

**Key settings:**
```python
# Resolution (set by TouchDesigner UI)
PRODUCTION_WIDTH = 1920
PRODUCTION_HEIGHT = 2160
TEST_WIDTH = 1138
TEST_HEIGHT = 1280

# Structures (trees)
STRUCTURES = [
    {'name': 'structure1', 'x': 0.3, 'y': 0.25, 'color': [255, 230, 100]},  # Yellow
    {'name': 'structure2', 'x': 0.7, 'y': 0.25, 'color': [255, 140, 180]},  # Pink
    {'name': 'structure3', 'x': 0.5, 'y': 0.75, 'color': [180, 120, 255]},  # Purple
]

# Visual parameters
AURA_DECAY_RATE = 0.998
AURA_GLOW_RADIUS = 18
TRAIL_MAX_POINTS = 80
TRAIL_FADE_RATE = 0.15
```

**Note:** Positions use normalized 0-1 coordinates (relative to canvas size).

---

## File Structure

```
biotelia-td/
├── biotelia-pollination.toe    # Main TouchDesigner project
├── config.py                    # Visual parameters & settings
├── pollination_system_current.py  # Main system logic
├── improved_rendering.py        # Rendering with watery trail effects
├── core/                        # Python modules
│   ├── system.py               # PollinationSystem orchestrator
│   ├── aura.py                 # Visitor aura (color absorption)
│   ├── trail.py                # Movement trails
│   ├── dance.py                # Pollination spiral effects
│   ├── structure.py            # Trees/structures
│   ├── agent.py                # Autonomous agents (disabled in prod)
│   └── mycelium.py             # Background network (unused)
├── docs/                        # Documentation
├── PRODUCTION_HANDOFF.md        # This file
├── DEPLOYMENT.md                # Deployment to new machines
└── MOCAP_SETUP.md               # Mocap integration details
```

---

## Production Checklist

Before going live:

### Hardware Setup
- [ ] Production machine has TouchDesigner Commercial license
- [ ] Mocap system is sending OSC to port 55556
- [ ] Network connection is stable
- [ ] Projector(s) configured for 1920×2160 output

### TouchDesigner Configuration
- [ ] Open `biotelia-pollination.toe`
- [ ] `/project1/settings_control` → Resmode = **Production 1920x2160**
- [ ] `/project1/settings_control` → Inputmode = **Mocap/OSC**
- [ ] `/project1/mocap/oscin1` → Port = **55556**
- [ ] Check textport shows: "PRODUCTION mode" and "0 agents (mocap mode)"

### Mocap Verification
- [ ] OSC channels visible: p0x, p0y, p0z, p1x, p1y, p1z, etc.
- [ ] Move in physical space → See position change in TouchDesigner
- [ ] Test all 9 visitor positions can be tracked
- [ ] Verify coordinate mapping (person at center → canvas center)

### Visual Verification
- [ ] See 3 colored structures rendering
- [ ] Visitors appear when mocap tracks movement
- [ ] Touching structure → Aura changes color
- [ ] Moving → Colored trails appear
- [ ] Touching different structure → Spiral pollination dance

### Performance
- [ ] Check frame rate (should be 60 FPS)
- [ ] Monitor CPU/GPU usage
- [ ] Verify no dropped frames during movement
- [ ] Test with maximum expected visitors (9 people)

---

## Troubleshooting

### No Visitors Appearing

**Check:**
1. OSC data is arriving (`/project1/mocap/oscin1` shows channels)
2. Settings are set to Mocap mode
3. Coordinate mapping is configured correctly
4. People are inside the projection area (7×8 ft centered zone)

**Fix:**
- Verify mocap system is sending to correct IP and port
- Check channel names match pattern: p0x, p0y, p1x, p1y, etc.
- Adjust coordinate mapping if positions seem wrong

### Visitors in Wrong Position

**Check:**
1. Mocap coordinate range (is it -1 to 1 or 0 to 1?)
2. Coordinate mapping parameters

**Fix:**
- Open `/project1/mocap` → "Coordinate Mapping"
- If mocap is 0-1: Set Input Range to "0to1" and recalculate Scale/Offset
- Test by having someone stand at known position (e.g., center)

### Module Import Errors

**Error:** "Cannot import 'core.system'" or similar

**Cause:** Project path not found

**Fix:**
1. Ensure `.toe` file is saved to disk in `biotelia-td` folder
2. Check textport for error message
3. Verify all files (core/, config.py, etc.) are in same folder
4. See DEPLOYMENT.md for details

### Old Rendering After git Pull

**Cause:** TouchDesigner caches embedded Python code

**Fix:**
1. Close TouchDesigner completely
2. `git pull` to get latest changes
3. Reopen TouchDesigner
4. OR: In textport, run module reload commands (see DEPLOYMENT.md)

---

## Performance Notes

**Current Performance:**
- 60 FPS rendering
- 1920×2160 resolution
- Up to 9 simultaneous visitors
- Watery flowing trail effects
- Real-time coordinate mapping

**Optimizations in place:**
- Vectorized numpy rendering (10-100x faster)
- GPU-accelerated composition in TouchDesigner
- Efficient trail fade algorithm
- Additive blending for glows

---

## Mocap Data Format

### Expected OSC Channels

```
/p0x - Person 0, X coordinate (-1 to 1)
/p0y - Person 0, Y coordinate (-1 to 1)
/p0z - Person 0, Z coordinate (ignored)
/p1x - Person 1, X coordinate
/p1y - Person 1, Y coordinate
/p1z - Person 1, Z coordinate (ignored)
...
/p8x - Person 8, X coordinate
/p8y - Person 8, Y coordinate
/p8z - Person 8, Z coordinate (ignored)
```

**Notes:**
- Z coordinate is received but ignored
- Only X and Y are used for positioning
- Range: -1 to 1 (center of room = 0)
- Port: 55556 (UDP)

---

## Support & Documentation

**Key Documentation Files:**
- `PRODUCTION_HANDOFF.md` (this file) - Production setup
- `DEPLOYMENT.md` - Moving to new machines
- `MOCAP_SETUP.md` - Detailed mocap integration
- `README.md` - Project overview

**For New Claude Code Session:**
Start with this file to understand the current production state.

**Git Repository:**
https://github.com/unforced/biotelia-td

**Contact:**
All changes committed with detailed commit messages.
Check git log for development history.

---

## What's NOT Included in Production

**Disabled/Removed:**
- ❌ Autonomous agents (bee, butterfly, moth) - only in test mode
- ❌ Mouse input - only for testing
- ❌ Data export nodes - removed (unused)
- ❌ Mycelial network - not currently rendered
- ❌ Old test scripts - cleaned up

**Production Mode:**
- ✅ Mocap-tracked visitors only
- ✅ Clean 14-node network
- ✅ No Python code editing needed on prod machine
- ✅ All tuning via TouchDesigner UI

---

## Emergency Reset

If something breaks:

1. **Reset to defaults:**
   - `/project1/settings_control` → Set both to Test/Mouse
   - Close and reopen TouchDesigner

2. **Clean reinstall:**
   ```bash
   cd /path/to/install
   rm -rf biotelia-td
   git clone https://github.com/unforced/biotelia-td.git
   ```

3. **Check git log for recent changes:**
   ```bash
   git log --oneline -10
   ```

---

**System Status:** ✅ Ready for Production
**Last Test:** 2025-11-25
**Deployment Target:** 7×8 ft centered projection in 20×30 ft room
