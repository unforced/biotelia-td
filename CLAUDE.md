# CLAUDE.md - AI Assistant Orientation Guide

**For:** New Claude Code sessions or AI assistants joining this project
**Last Updated:** 2025-11-28
**Project Status:** Ready for Live Testing - Coordinate Mapping Configured

---

## TL;DR - Where We're At

This is a TouchDesigner pollination visualization for an **18×15 ft floor projection**. Visitors are tracked via mocap and become pollinators in an interactive ecosystem. Coordinate mapping is configured and ready for live testing.

**Current State:**
- TouchDesigner file: `biotelia-pollination.toe`
- Resolution: **2160×1920** (landscape - X is wider)
- Input: Mocap/OSC (9 visitors, port 55556)
- Coordinate mapping: **Configured** - needs live testing to verify
- Python DATs: **Linked to external files** (auto-sync)
- Mocap chain: **Simplified** - clean sequential signal flow

**Testing Status:**
- Visitor indicators enlarged 10x for visibility during testing
- Ready for live mocap testing to verify axis alignment
- May need axis inversion adjustments based on testing

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

### Mocap Signal Chain (VERIFIED 2025-11-28)

```
oscin1 → math4 → o1to9 → math3 → map_x → map_y → momentum → out1
           │        │       │        │       │         │
           │        │       │        │       │         └── smoothing/lag
           │        │       │        │       └── scope *y: (val+0.32)×-2206.9+1920
           │        │       │        └── scope *x: (val+0.35)×2482.76
           │        │       └── negates X channels (scope o*_x)
           │        └── renames qtm/6d/trk_[1-9] to p[1-9][xyz]
           └── gain 0.0002 (scales raw mm to ~±0.5 range)
```

**Key:** Sequential chain - each Math CHOP with scope passes through non-matching channels unchanged. No split/merge pattern needed.

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

## Coordinate Mapping (CONFIGURED)

### Full Pipeline

```
Mocap (raw mm) → math4 (×0.0002) → ... → map_x/map_y (to pixels) → Python (final adjustments)
```

| Stage | X Channels | Y Channels |
|-------|------------|------------|
| Raw mocap | ~thousands (mm) | ~thousands (mm) |
| After math4 | ~±0.5 | ~±0.5 |
| After map_x | `(val+0.35)×2482.76` → 0-2160 px | pass through |
| After map_y | pass through | `(val+0.32)×-2206.9+1920` → 0-1920 px |
| Python | `2160 - x_val` (invert) | `y_val` (direct) |

### TouchDesigner Parameters

**`/project1/mocap/map_x`:**
- preoff: 0.35
- gain: 2482.76
- scope: `*x`

**`/project1/mocap/map_y`:**
- preoff: 0.32
- gain: -2206.9
- postoff: 1920
- scope: `*y`

### Python Mapping (pollination_system_current.py:164-168)

```python
visitors.append({
    'id': person_id - 1,
    'x': 2160 - x_val,  # invert X: high phys X → low screen X
    'y': y_val,         # direct: high phys Y → high screen Y
})
```

### Expected Behavior (after testing)

- Walking toward **high X** (physical) → move **left** on screen
- Walking toward **high Y** (physical) → move **down** on screen
- Yellow structure: **bottom-left** of projection = **high X, high Y** in physical space

### Testing Visibility

Currently **10x enlarged** for testing:
- Visitor rings: 140px radius (normal: 14px)
- Auras: 10x scale multiplier

**To restore normal sizes after testing:**
1. Edit `improved_rendering.py` line 136: remove `* 10`
2. Edit `improved_rendering.py` line 168: change `140, 120` to `14, 12`

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
- Removed `select_y` and `replace_xy` nodes (were creating janky split/merge pattern)
- Chain is now clean sequential: `math3 → map_x → map_y → momentum → out1`
- Each Math CHOP scopes only its channels, passes others through unchanged

### Python DAT Linking
- `pollination_system` DAT linked to `pollination_system_current.py`
- `optimized_circles_callbacks` DAT linked to `improved_rendering.py`
- Changes to .py files auto-sync to TD

### Coordinate Mapping Fixes
- Fixed channel names: `p1x` not `p0x` (mocap channels start at 1)
- Removed double-scaling bug (Python was multiplying by canvas size, but TD already outputs pixels)
- Added X-axis inversion in Python (`2160 - x_val`)
- Configured map_x/map_y with measured projection boundaries

### Testing Enhancements
- Enlarged visitor indicators 10x (140px radius) for visibility during testing
- Enlarged auras 10x

### Cleanup
- Removed orphan nodes: `input_selector`, `frame_timer`, `animation_driver`, `frame_timer_callbacks1`, `frame_speed`, `trail1`, `select_y`, `replace_xy`

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

### Immediate (Live Testing Required)

1. **Test coordinate mapping with mocap**
   - Walk in projection area, observe visitor indicator movement
   - Verify: physical up → screen up, physical left → screen left
   - Note any axis swaps or inversions needed

2. **If axes are wrong**, adjust in `pollination_system_current.py` lines 164-168:
   - Swap X/Y: `'x': y_val, 'y': x_val`
   - Invert X: `'x': 2160 - x_val`
   - Invert Y: `'y': 1920 - y_val`

3. **Once aligned**, restore normal sizes in `improved_rendering.py`:
   - Line 136: remove `* 10` from aura radius
   - Line 168: change `140, 120` to `14, 12` for visitor rings

### After Testing Passes

4. Fine-tune projection boundaries if needed (adjust map_x/map_y preoff and gain)
5. Test with multiple visitors
6. Verify pollination mechanics (color absorption, trails, dances)

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

## Troubleshooting Coordinate Mapping

### Movement is inverted (e.g., walk left → goes right)

Edit `pollination_system_current.py` lines 164-168:
```python
# To invert X axis:
'x': 2160 - x_val,  # instead of just x_val

# To invert Y axis:
'y': 1920 - y_val,  # instead of just y_val
```

### Axes are swapped (e.g., walk left → goes up)

Edit `pollination_system_current.py` lines 164-168:
```python
# Swap X and Y:
'x': y_val,
'y': x_val,

# Or with inversions:
'x': 1920 - y_val,
'y': 2160 - x_val,
```

### Position is offset (visitor appears in wrong location)

Adjust TouchDesigner `map_x`/`map_y` parameters:
- **preoff**: Shifts the input range (add to move projection area)
- **gain**: Scales the range (increase to stretch, decrease to compress)
- **postoff**: Shifts the output (add to move output position)

### Debug: Check raw vs mapped values

```python
# In TD textport or via MCP:
raw = op('/project1/mocap/math3').chan('p1x').eval()
mapped = op('/project1/input_switch').chan('p1x').eval()
print(f"Raw: {raw}, Mapped: {mapped}")
```

### Visitor not appearing at all

1. Check mocap OSC is arriving: look at `/project1/mocap/oscin1` channels
2. Check `input_switch` is outputting values in 0-2160/0-1920 range
3. Check Python is parsing channels correctly (p1x, not p0x)

---

**This file is the starting point for any new AI assistant session.**

For production deployment details, see `PRODUCTION_HANDOFF.md`.
For mocap setup details, see `MOCAP_SETUP.md`.
