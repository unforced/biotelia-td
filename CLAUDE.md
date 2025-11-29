# CLAUDE.md - AI Assistant Orientation Guide

**For:** New Claude Code sessions or AI assistants joining this project
**Last Updated:** 2025-11-28
**Project Status:** Ready for Live Testing - Coordinate Mapping Simplified

---

## TL;DR - Where We're At

This is a TouchDesigner pollination visualization for an **18×15 ft floor projection**. Visitors are tracked via mocap and become pollinators in an interactive ecosystem.

**Current State:**
- TouchDesigner file: `biotelia-pollination.toe`
- Resolution: **1920×2160** (portrait - production) or **1138×1280** (test mode)
- Input: Mocap/OSC (9 visitors, port 55556)
- Coordinate mapping: **Done in TD** - raw mm → pixels via Range mapping
- Python DATs: **Linked to external files** (auto-sync)
- Mocap chain: **Clean and simple** - direct signal flow

**Testing Status:**
- Visitor indicators enlarged 10x for visibility during testing
- Ready for live mocap testing to verify axis alignment
- Adjust map_x/map_y Range parameters if positioning is off

---

## Physical Setup

- **Room:** 34 ft (X) × 45 ft (Y)
- **Projection:** 18 ft (X) × 15 ft (Y), centered
  - 8 ft padding on each side in X
  - 15 ft padding on each side in Y
- **Canvas:** 1920 px (X) × 2160 px (Y) in production mode
- **Mocap:** Sends raw values in millimeters (mm)

**Approximate Mocap Coordinate Ranges (mm):**
- X: -1750 to 2600 (projection area)
- Y: -2750 to 1600 (projection area)

---

## Architecture Overview

### TouchDesigner Network

**Key Nodes at `/project1`:**
- `mocap` - COMP with OSC input + coordinate mapping chain
- `input_switch` - Passes mocap data (index=0 for mocap mode)
- `pollination_system` - Python DAT (linked to `pollination_system_current.py`)
- `gpu_renderer` - Rendering COMP with scriptTOP
- `settings_control` - UI parameters (Resmode, Inputmode)
- `mcp_webserver_base` - MCP server for Claude Code control

### Mocap Signal Chain

```
oscin1 → o1to9 → map_x → map_y → momentum → out1
           │        │       │         │
           │        │       │         └── lag smoothing (0.1s)
           │        │       └── Range: mm → pixels (Y axis)
           │        └── Range: mm → pixels (X axis)
           └── renames qtm/6d/trk_[1-9][1-3] to p[1-9][xyz]
```

**Key:** All coordinate mapping happens in TouchDesigner. Python receives pixel coordinates directly.

### Coordinate Mapping (map_x / map_y)

Both use **Range** mode (`postop = range`) to convert raw mm to pixels:

**`/project1/mocap/map_x`:**
- fromrange1: -1750 (left edge in mm)
- fromrange2: 2600 (right edge in mm)
- torange1: 0 (left edge in pixels)
- torange2: 2160 (right edge in pixels)
- scope: `*x`

**`/project1/mocap/map_y`:**
- fromrange1: -2750 (one edge in mm)
- fromrange2: 1600 (other edge in mm)
- torange1: 1920 (inverted mapping)
- torange2: 0
- scope: `*y`

**To adjust mapping:** Change fromrange1/fromrange2 values based on actual mocap coordinate observations.

### Python Files (LINKED to DATs)

Both Python files are **synced to external files** - edits auto-update in TD:

| DAT | External File | Purpose |
|-----|---------------|---------|
| `/project1/pollination_system` | `pollination_system_current.py` | System logic |
| `/project1/gpu_renderer/optimized_circles_callbacks` | `improved_rendering.py` | Rendering |

**To force reload after editing:**
```python
import sys
for mod in list(sys.modules.keys()):
    if 'pollination' in mod or 'core' in mod:
        del sys.modules[mod]
op('/project1/pollination_system').par.loadonstartpulse.pulse()
op('/project1/gpu_renderer/optimized_circles').cook(force=True)
```

---

## Resolution System

Resolution is **dynamic** based on `settings_control.Resmode`:

| Mode | Width | Height | Notes |
|------|-------|--------|-------|
| production | 1920 | 2160 | Requires commercial TD license |
| test | 1138 | 1280 | Within non-commercial 1280×1280 limit |

The following nodes use expressions to match:
- `optimized_circles` (scriptTOP) - sets the resolution
- `background` (constantTOP) - references scriptTOP
- `composite` (compositeTOP) - references scriptTOP

---

## Channel Naming

**Important:** Mocap channels start at **1**, not 0:
- `p1x`, `p1y`, `p1z` - Person 1
- `p2x`, `p2y`, `p2z` - Person 2
- ... up to `p9x`, `p9y`, `p9z`

The Python code iterates `range(1, MAX_VISITORS + 1)` to match.

---

## Recent Changes (2025-11-28)

### Coordinate Mapping Overhaul
- **Removed** arbitrary 0.0001 scaling (math4 deleted)
- **Removed** broken math3 node (wrong scope pattern)
- **Using** Range mapping in map_x/map_y: raw mm → pixels directly
- **Removed** Python-side coordinate manipulation (was `2160 - x_val`)
- All mapping now happens in TouchDesigner for better performance

### Resolution Made Dynamic
- scriptTOP, composite, background now use expressions
- Automatically adapts to production/test mode via settings_control

### Momentum Simplified
- Removed complex slope/filter/math chain
- Now just: `in1 → lag1 (0.1s) → out1`
- Simple smoothing for responsive but stable tracking

### Orphan Nodes Removed
- Deleted: `math3`, `math4`, `optimized_circles_callbacks1`, `update_pulse`
- Cleaned up momentum COMP internals

### Files Archived
Moved to `archive/` directory:
- `frame_timer_callbacks.py`
- `standalone.py`
- `run_animation_td.py`
- `render/` directory
- `input/` directory

---

## Quick Reference

### Check Mocap Data Flow
```python
# Raw mm values (after channel rename):
op('/project1/mocap/o1to9').chan('p1x').eval()  # Should be ~-1000 to +1000

# After pixel mapping:
op('/project1/input_switch').chan('p1x').eval()  # Should be ~0-2160
op('/project1/input_switch').chan('p1y').eval()  # Should be ~0-1920
```

### Test Visitor Detection
```python
ps = op('/project1/pollination_system')
chop = op('/project1/input_switch')
result = ps.module.update_frame(chop, 1/60)
len(result['visitors'])  # Should show number of detected visitors
```

### Force Render Update
```python
op('/project1/gpu_renderer/optimized_circles').cook(force=True)
```

---

## Files to Know

| File | Purpose |
|------|---------|
| `biotelia-pollination.toe` | Main TD project |
| `pollination_system_current.py` | Visitor tracking, auras, trails |
| `improved_rendering.py` | GPU rendering (scriptTOP callback) |
| `config.py` | Visual parameters, structure positions |
| `core/system.py` | PollinationSystem class |
| `core/aura.py`, `trail.py`, `dance.py` | Component logic |

---

## Next Steps

### Immediate (Live Testing Required)

1. **Test coordinate mapping with mocap**
   - Walk in projection area, observe visitor indicator movement
   - Verify: physical movement maps correctly to screen movement

2. **If positioning is wrong**, adjust map_x/map_y Range parameters:
   - `fromrange1`/`fromrange2`: Adjust to match actual mocap mm values
   - Swap torange1/torange2 to invert an axis

3. **Once aligned**, restore normal sizes in `improved_rendering.py`:
   - Line 136: remove `* 10` from aura radius
   - Line 168: change `140, 120` to `14, 12` for visitor rings

### After Testing Passes

4. Fine-tune projection boundaries (adjust fromrange values)
5. Test with multiple visitors
6. Verify pollination mechanics (color absorption, trails, dances)

---

## Troubleshooting Coordinate Mapping

### Movement is inverted (e.g., walk left → goes right)

Swap the `torange1` and `torange2` values in map_x or map_y:
```python
# Via MCP:
op('/project1/mocap/map_x').par.torange1 = 2160  # was 0
op('/project1/mocap/map_x').par.torange2 = 0     # was 2160
```

### Axes are swapped (e.g., walk left → goes up)

The map_x scope is `*x` and map_y scope is `*y`. If axes seem swapped, check if the mocap system has X/Y conventions different from expected.

### Position is offset (visitor appears in wrong location)

Adjust the `fromrange1`/`fromrange2` values to match actual mocap coordinates:
```python
# Check actual raw values first:
print(op('/project1/mocap/o1to9').chan('p1x').eval())
print(op('/project1/mocap/o1to9').chan('p1y').eval())

# Then adjust range to encompass observed values
```

### Visitor not appearing at all

1. Check mocap OSC is arriving: `op('/project1/mocap/oscin1').numChans`
2. Check channels are renamed: `op('/project1/mocap/o1to9').chans()`
3. Check pixel output is in valid range: 0-2160 for X, 0-1920 for Y

---

## MCP Server

Claude Code can control TD via MCP server at `/project1/mcp_webserver_base`:
- Execute Python scripts
- Read/update node parameters
- Create/delete nodes
- Get node info

**Connection:** Pulse the webserver to restart if connection lost after TD restart.

---

## Git Workflow

```bash
# After making changes in TD, save the .toe file, then:
git add biotelia-pollination.toe
git commit -m "Description of changes"
git push

# Python file changes are tracked separately:
git add pollination_system_current.py improved_rendering.py
git commit -m "Description"
git push
```

**Note:** Development machine and production machine use same repo. Pull on prod to get updates.

---

**This file is the starting point for any new AI assistant session.**

For production deployment details, see `PRODUCTION_HANDOFF.md`.
For mocap setup details, see `MOCAP_SETUP.md`.
