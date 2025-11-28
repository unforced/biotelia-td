# CLAUDE.md - AI Assistant Orientation Guide

**For:** New Claude Code sessions or AI assistants joining this project
**Last Updated:** 2025-11-28
**Project Status:** In Active Development - Coordinate Mapping Refinement

---

## TL;DR - Where We're At

This is a TouchDesigner pollination visualization for an **18×15 ft floor projection**. Visitors are tracked via mocap and become pollinators in an interactive ecosystem. Currently refining the coordinate mapping between physical space and screen space.

**Current State:**
- TouchDesigner file: `biotelia-pollination.toe`
- Resolution: **2160×1920** (landscape - X is wider)
- Input: Mocap/OSC (9 visitors, port 55556)
- Coordinate mapping: **Being refined** - axes alignment in progress
- Python DATs: **Linked to external files** (auto-sync)

**Active Work:**
- Aligning physical room movement to screen movement
- Testing with enlarged visitor indicators (10x size for visibility)
- May need axis inversion adjustments

---

## Physical Setup (UPDATED)

- **Room:** 34 ft (X) × 45 ft (Y)
- **Projection:** 18 ft (X) × 15 ft (Y), centered
  - 8 ft padding on each side in X
  - 15 ft padding on each side in Y
- **Canvas:** 2160 px (X) × 1920 px (Y)
- **Mocap:** Sends values scaled by 0.0002 (raw values in thousands, likely mm)

**Projection Corners in Mocap Space (after math4 scaling):**
- Top-left: X=-0.35, Y=0.32
- Top-right: X=0.52, Y=0.32
- Bottom-left: X=-0.35, Y=-0.55
- Bottom-right: X=0.52, Y=-0.55

**Structure Positions (physical room, observed):**
- Yellow: Bottom-left on screen = High X, High Y in physical space
- Pink: Bottom-right on screen
- Purple: Top-center on screen

---

## Architecture Overview

### TouchDesigner Network

**Key Nodes at `/project1`:**
- `mocap` - COMP with OSC input + coordinate mapping chain
- `input_switch` - Passes mocap data (index=0 for mocap mode)
- `pollination_system` - Python DAT (linked to `pollination_system_current.py`)
- `gpu_renderer` - Rendering COMP with scriptTOP
- `settings_control` - UI parameters
- `mcp_webserver_base` - MCP server for Claude Code control
- `update_pulse` - Timing

### Mocap Signal Chain (SIMPLIFIED 2025-11-28)

```
oscin1 → math4 → o1to9 → math3 → map_x → map_y → momentum → out1
           │        │       │        │       │
           │        │       │        │       └── scope *y, transforms Y channels
           │        │       │        └── scope *x, transforms X channels
           │        │       └── negates X channels (scope o*_x)
           │        └── renames qtm/6d/trk_[1-9] to p[1-9][xyz]
           └── gain 0.0002 (scales raw mm to ~±0.5 range)
```

**Note:** Sequential chain - each Math CHOP with scope passes through non-matching channels unchanged. No split/merge needed.

### Python Files (LINKED to DATs)

Both Python files are now **synced to external files** - edits to the .py files automatically update in TD:

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

## Coordinate Mapping (CURRENT WORK)

### The Challenge

Physical movement in the room needs to map correctly to screen movement. Currently working on:
1. **Axis alignment** - Which mocap axis maps to which screen axis
2. **Inversions** - Direction of movement (up=up, left=left)
3. **Scale/offset** - Mapping projection boundaries to canvas pixels

### Current Mapping Formula

**In TouchDesigner (`map_x` and `map_y` nodes):**
- `map_x`: preoff=0.35, gain=2482.76 (scope *x)
- `map_y`: preoff=0.32, gain=-2206.9, postoff=1920 (scope *y)

**In Python (`pollination_system_current.py`):**
```python
# Current mapping (may need adjustment):
'x': 2160 - x_val,  # invert X
'y': y_val,
```

### Testing

Visitor indicators are currently **10x enlarged** for testing visibility:
- Yellow rings: 140px radius (normally 14px)
- Auras: 10x scale multiplier

### Known Issues

- Physical movement may not align perfectly with screen movement
- May need to swap X/Y axes or add inversions
- Test by walking and observing which direction visitor moves

---

## Channel Naming

**Important:** Mocap channels start at **1**, not 0:
- `p1x`, `p1y`, `p1z` - Person 1
- `p2x`, `p2y`, `p2z` - Person 2
- ... up to `p9x`, `p9y`, `p9z`

The Python code iterates `range(1, MAX_VISITORS + 1)` to match.

---

## Recent Changes (2025-11-28)

### Mocap Chain Simplification
- Removed `select_y` and `replace_xy` nodes
- Chain is now sequential: map_x → map_y (each transforms its scoped channels)

### Python DAT Linking
- `pollination_system` DAT linked to `pollination_system_current.py`
- `optimized_circles_callbacks` DAT linked to `improved_rendering.py`
- Changes to .py files auto-sync to TD

### Coordinate Mapping Fixes
- Fixed channel names (p1x not p0x)
- Removed double-scaling bug (TD already maps to pixels)
- Added X-axis inversion in Python
- Testing axis alignment

### Cleanup
- Removed orphan nodes: `input_selector`, `frame_timer`, `animation_driver`, `frame_timer_callbacks1`, `frame_speed`, `trail1`

---

## Quick Reference

### Check Mocap Data Flow
```python
# In TD textport or via MCP:
op('/project1/input_switch').chan('p1x').eval()  # Should be ~0-2160 range
op('/project1/input_switch').chan('p1y').eval()  # Should be ~0-1920 range
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

1. **Test coordinate mapping** - Walk around, verify movement direction
2. **Adjust inversions** - If axes are wrong, modify Python mapping
3. **Restore normal sizes** - Once aligned, remove 10x scaling
4. **Fine-tune boundaries** - Ensure projection edges map correctly

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
