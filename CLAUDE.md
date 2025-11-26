# CLAUDE.md - AI Assistant Orientation Guide

**For:** New Claude Code sessions or AI assistants joining this project
**Last Updated:** 2025-11-25
**Project Status:** ✅ Production Ready - Mocap Mode

---

## TL;DR - Where We're At

This is a **working, production-ready** TouchDesigner pollination visualization for a 7×8 ft floor projection. Visitors are tracked via mocap and become pollinators in an interactive ecosystem. The system is **complete and deployed**.

**Current State:**
- ✅ TouchDesigner file: `biotelia-pollination.toe`
- ✅ Resolution: 1920×2160 (portrait)
- ✅ Input: Mocap/OSC (9 visitors, port 55556)
- ✅ Coordinate mapping: Pre-configured for room layout
- ✅ Network: Clean, organized, production-focused
- ✅ Documentation: Comprehensive

**If starting fresh:** Read `PRODUCTION_HANDOFF.md` first for complete production setup.

---

## Project Purpose

Interactive floor projection where visitors become pollinators in a living ecosystem:

1. **Touch a structure** (glowing tree) → Your aura absorbs its color
2. **Move through space** → Leave colored trails that fade
3. **Touch different structure** → Spiral pollination dance effect
4. **Visual metaphor** → Cross-pollination between different colored "trees"

**Physical Setup:**
- Room: 20 ft × 30 ft
- Projection: 7 ft × 8 ft (centered)
- Mocap tracks up to 9 people
- Mocap sends OSC data (-1 to 1 range)

---

## Architecture Overview

### The Stack

```
Mocap System (OSC) → TouchDesigner → Projector
                          ↓
                    Python Logic
                    (core/*.py)
                          ↓
                    GPU Rendering
                    (1920×2160)
```

### TouchDesigner Network (14 nodes)

**Input & Settings:**
- `settings_control` - UI for Resolution/Input mode
- `mocap` - COMP with OSC input + coordinate mapping
- `input_switch` - Mode switching

**Core:**
- `pollination_system` - Python logic (visitor tracking, auras, trails)
- `gpu_renderer` - Rendering COMP (output)

**Timing:**
- `frame_timer`, `frame_speed`, `animation_driver`, `update_pulse`

**Utilities:**
- `mcp_webserver_base` - MCP server for remote control
- `python_path`, `setup_python_path` - Dynamic path resolution

### Python Modules

```
core/
├── system.py       # PollinationSystem (orchestrator)
├── aura.py         # VisitorAura (color absorption from structures)
├── trail.py        # MovementTrail (fading colored trails)
├── dance.py        # PollinationDance (spiral particle effects)
├── structure.py    # Structure (trees with colors)
└── agent.py        # AutonomousAgent (disabled in production)
```

**Main entry points:**
- `pollination_system_current.py` - DAT that runs the system
- `improved_rendering.py` - Rendering with watery trail effects

---

## Key Concepts

### 1. Structures (Trees)

Static colored circles at fixed positions. Defined in `config.py`:

```python
STRUCTURES = [
    {'name': 'structure1', 'x': 0.3, 'y': 0.25, 'color': [255, 230, 100]},  # Yellow
    {'name': 'structure2', 'x': 0.7, 'y': 0.25, 'color': [255, 140, 180]},  # Pink
    {'name': 'structure3', 'x': 0.5, 'y': 0.75, 'color': [180, 120, 255]},  # Purple
]
```

**Positions:** Normalized 0-1 coordinates (scales to any resolution)

### 2. Visitor Auras

Each visitor has an aura that:
- Starts neutral/colorless
- Absorbs color when touching a structure
- Slowly fades over time (`AURA_DECAY_RATE = 0.998`)
- Renders as glowing circle around visitor

### 3. Movement Trails

Distance-based trail system:
- Adds trail point when visitor moves > threshold distance
- Max 80 points (`TRAIL_MAX_POINTS`)
- Each point fades over time (`TRAIL_FADE_RATE = 0.15`)
- Renders with "watery flow" animation (undulating sine waves)

### 4. Pollination Dances

Triggered when visitor carrying color A touches structure with color B:
- Spiral particle effect
- Color transitions from A → B
- Visual "cross-pollination" metaphor

### 5. Coordinate Mapping

Critical system for mapping mocap coordinates to canvas:

**Formula:** `canvas = (mocap × Scale) + Offset`

**Current config (in `/project1/mocap`):**
- X Scale: 2742.86, X Offset: 960
- Y Scale: 4050, Y Offset: 1080
- Input Range: -1 to 1

**Why:** Maps 7×8 ft projection area (centered in 20×30 ft room) to 1920×2160 canvas.

---

## Configuration Files

### `config.py` - Visual Parameters

All visual settings in one place:

```python
# Resolution
PRODUCTION_WIDTH = 1920
PRODUCTION_HEIGHT = 2160

# Structures
STRUCTURES = [...]  # 3 colored trees

# Visual parameters
AURA_DECAY_RATE = 0.998
AURA_GLOW_RADIUS = 18
TRAIL_MAX_POINTS = 80
TRAIL_FADE_RATE = 0.15
TRAIL_MIN_DISTANCE = 8
```

### TouchDesigner Settings (`/project1/settings_control`)

**Resmode:**
- `Test 1138x1280` - For testing
- `Production 1920x2160` - **Active**

**Inputmode:**
- `Mouse/Test` - For development
- `Mocap/OSC` - **Active**

### Mocap Settings (`/project1/mocap`)

**Coordinate Mapping page:**
- X Scale, X Offset, Y Scale, Y Offset
- Input Range (0-1 or -1 to 1)
- **Tunable in production without code changes**

---

## Data Flow

### Frame Update Cycle

1. **Mocap sends OSC** → `/project1/mocap/oscin1` (port 55556)
   - Channels: p0x, p0y, p0z, p1x, p1y, p1z, ... p8x, p8y, p8z

2. **Coordinate mapping** → `/project1/mocap/map_x`, `map_y`, `merge_xy`
   - Transforms mocap coords to canvas pixels

3. **Python logic** → `pollination_system` DAT
   - Parses visitor positions
   - Updates auras (color absorption, decay)
   - Updates trails (add points, fade)
   - Checks for pollination (collision with structures)
   - Creates pollination dances

4. **Rendering** → `improved_rendering.py` in scriptTOP
   - Draws all layers to numpy array (1920×2160 RGBA)
   - Background → Structures → Trails → Auras → Visitors → Dances

5. **Output** → `/project1/gpu_renderer/OUT`

### Rendering Layers (back to front)

1. **Background** - Dark forest floor (10, 15, 8 RGB)
2. **Structures** - Glowing colored circles with cores
3. **Trails** - Watery flowing particle trails
4. **Visitor Auras** - Colored glows around visitors
5. **Visitor Indicators** - Yellow rings
6. **Pollination Dances** - Spiral particle effects

**Blending:**
- Structures, visitors: Alpha blending
- Trails, auras, dances: Additive blending (glows)

---

## Mode Switching

### Production vs Test Mode

**Test Mode:**
- Resolution: 1138×1280 (fits in non-commercial TD limit)
- Input: Mouse
- Autonomous agents: 3 (bee, butterfly, moth)

**Production Mode (Current):**
- Resolution: 1920×2160
- Input: Mocap/OSC
- Autonomous agents: None (mocap-only)

**How to switch:**
- Open `/project1/settings_control`
- Change Resmode and Inputmode parameters
- System reinitializes automatically

---

## Recent Major Changes

### Network Cleanup (2025-11-25)
- Removed 11 unused nodes (25 → 14)
- Deleted: test inputs, data export nodes, duplicates
- Organized into logical horizontal rows

### Coordinate Mapping System (2025-11-25)
- Added tunable parameters to `/project1/mocap`
- Pre-configured for 7×8 ft projection in 20×30 ft room
- Supports both 0-1 and -1 to 1 mocap ranges

### Settings UI (2025-11-25)
- Created `/project1/settings_control` for production
- Resmode and Inputmode parameters
- No Python editing needed on prod machine

### Path Resolution (2025-11-25)
- Dynamic path using `project.folder`
- No hardcoded paths - fail fast if not found
- Works on any machine/username

### Autonomous Agent Removal (2025-11-25)
- Disabled bee/butterfly/moth in mocap mode
- Production shows only mocap-tracked visitors

---

## Common Tasks

### Adding a New Structure

1. Edit `config.py`:
```python
STRUCTURES = [
    # ... existing structures
    {'name': 'structure4', 'x': 0.5, 'y': 0.5, 'color': [100, 255, 180]},  # Cyan
]
```

2. Reload TouchDesigner or force module reload

**Note:** Use normalized 0-1 coordinates (0.5 = center)

### Adjusting Visual Parameters

Edit `config.py`:
- Trail length: `TRAIL_MAX_POINTS`
- Trail fade: `TRAIL_FADE_RATE`
- Aura size: `AURA_GLOW_RADIUS`
- Aura persistence: `AURA_DECAY_RATE`

### Tuning Coordinate Mapping

1. Open `/project1/mocap`
2. Go to "Coordinate Mapping" page
3. Adjust Scale/Offset parameters
4. Test with known positions

**Example:** Person at center (0, 0) should map to canvas center (960, 1080)

### Debugging Mocap Input

1. Check `/project1/mocap/oscin1` - Are channels appearing?
2. Check channel values - Moving when person moves?
3. Check coordinate mapper output - Reasonable pixel values?
4. Check pollination_system - Are visitors being created?

---

## File Organization

### Root Files
```
biotelia-pollination.toe       # Main TD project ⭐
config.py                       # Visual parameters
pollination_system_current.py  # System logic entry
improved_rendering.py           # Rendering entry
```

### Documentation
```
PRODUCTION_HANDOFF.md   # Production setup guide ⭐
CLAUDE.md               # This file
DEPLOYMENT.md           # Moving to new machines
MOCAP_SETUP.md          # Mocap integration details
README.md               # Project overview
```

### Code Modules
```
core/
├── system.py      # Main orchestrator
├── aura.py        # Visitor aura logic
├── trail.py       # Trail system
├── dance.py       # Pollination dances
├── structure.py   # Trees/structures
└── agent.py       # Autonomous agents (unused in prod)
```

---

## Performance

**Current:**
- 60 FPS at 1920×2160
- Up to 9 simultaneous visitors
- CPU rendering (numpy)
- GPU composition (TouchDesigner TOPs)

**Optimizations:**
- Vectorized numpy operations (10-100x faster)
- Efficient trail fade algorithm
- Additive blending for glows
- Limited trail points (80 max per visitor)

---

## Deployment Notes

### Dynamic Path Resolution

System uses `project.folder` to find Python modules:
- Works on any machine/username
- No hardcoded paths
- Fails fast with clear error if `.toe` not saved properly

### Git Workflow

```bash
# Pull latest changes
git pull

# Changes are embedded in .toe file
# Close and reopen TouchDesigner to see updates
```

### Module Reloading

If Python code changes without restarting TD:

```python
# In textport:
import sys
for mod in list(sys.modules.keys()):
    if 'core' in mod or 'pollination' in mod:
        del sys.modules[mod]

op('/project1/pollination_system').module.initialized = False
op('/project1/pollination_system').cook(force=True)
```

---

## Troubleshooting Quick Reference

### No Visitors Visible
- Check mocap OSC input arriving
- Verify Inputmode = "Mocap/OSC"
- Check coordinate mapping (people in projection area?)

### Wrong Positions
- Verify mocap range (-1 to 1 vs 0 to 1)
- Adjust coordinate mapping parameters
- Test with person at known position

### Import Errors
- Ensure `.toe` saved to disk in biotelia-td folder
- Check all files (core/, config.py) present
- See DEPLOYMENT.md

### Old Code After Update
- Close TouchDesigner completely
- Pull latest from git
- Reopen TouchDesigner

---

## What NOT to Do

❌ **Don't edit Python code on production machine** - Use TouchDesigner UI parameters
❌ **Don't commit the .toe file carelessly** - Contains embedded code, gets large
❌ **Don't use hardcoded paths** - Use dynamic resolution
❌ **Don't enable autonomous agents in mocap mode** - Production is mocap-only
❌ **Don't assume 0-1 mocap range** - Verify range first (-1 to 1 currently)

---

## Next Steps for New Session

1. **Read PRODUCTION_HANDOFF.md** - Complete production setup guide
2. **Check current git status** - See what's changed recently
3. **Open TouchDesigner file** - Verify system running
4. **Review recent commits** - `git log --oneline -10`
5. **Ask about current priorities** - What needs work?

---

## Key Decisions Made

### Architecture
✅ Python logic + TouchDesigner rendering (hybrid approach)
✅ Dynamic path resolution (works on any machine)
✅ Mocap-only in production (no autonomous agents)
✅ OSC input on port 55556

### Configuration
✅ 1920×2160 resolution (portrait 8:9 aspect)
✅ 3 structures (can add more in config.py)
✅ Coordinate mapping for 7×8 ft centered projection
✅ -1 to 1 mocap range

### Visual Design
✅ Watery flowing trails (sine wave animation)
✅ Additive blending for glows
✅ Dark forest floor background
✅ Pollination dances on color change

---

## Contact & History

**Repository:** https://github.com/unforced/biotelia-td

**Development Timeline:**
- Initial Python prototype
- TouchDesigner integration
- Performance optimization (10-100x improvement)
- Mocap integration
- Production configuration
- Network cleanup
- Coordinate mapping system

**Current Status:** Production Ready
**Last Major Update:** 2025-11-25

---

**This file is the starting point for any new AI assistant session.**

For production deployment details, see `PRODUCTION_HANDOFF.md`.
For mocap setup, see `MOCAP_SETUP.md`.
For deployment to new machines, see `DEPLOYMENT.md`.
