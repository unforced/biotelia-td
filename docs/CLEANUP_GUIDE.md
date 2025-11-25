# Network Cleanup Guide

**Problem:** Multiple implementations blended together
**Solution:** Delete unused nodes from experiments

---

## ✓ KEEP THESE (9 essential nodes)

### Input (2 nodes)
- ✓ `mouse_input` - Captures mouse position
- ✓ `scale_to_canvas` - Scales to 1920x1080

### Logic (4 nodes)
- ✓ `pollination_system` - Core Python logic
- ✓ `frame_timer` - 60 FPS clock
- ✓ `frame_timer_callbacks1` - Timer triggers
- ✓ `hybrid_data_exporter` - Exports to tables

### Data (4 nodes)
- ✓ `structures_data` - Tree data table
- ✓ `visitors_data` - Visitor data table
- ✓ `trails_data` - Trail data table
- ✓ `particles_data` - Particle data table

### Output (1 node)
- ✓ `gpu_renderer` ⭐ - Optimized renderer

### Utilities (optional)
- ✓ `python_path` - Python path setup
- ✓ `setup_python_path` - Python initialization
- ✓ `mcp_webserver_base` - MCP server (if using remote control)

---

## ❌ DELETE THESE (old experiments)

### Old Renderers
- ❌ `hybrid_render` - Replaced by gpu_renderer
- ❌ `hybrid_render_callbacks1` - Old render code
- ❌ `pollination_render` - Even older renderer
- ❌ `pollination_render_callbacks` - Even older code
- ❌ `hybrid_renderer` (base COMP if exists) - Old container

### Unused Script CHOPs (don't work)
- ❌ `structures_chop`
- ❌ `visitors_chop`
- ❌ `trails_chop`
- ❌ `particles_chop`

### Unused Callbacks
- ❌ `structures_chop_callbacks` (or `structures_chop_callbacks1`)
- ❌ `visitors_chop_callbacks`
- ❌ `trails_chop_callbacks`
- ❌ `particles_chop_callbacks`

### Old Prototypes
- ❌ `native_prototype` - Early experiment (entire component)

---

## How to Clean Up

### Option 1: Manual Delete (Safest)
1. In TouchDesigner, select each node marked ❌
2. Press Delete
3. Repeat for all unused nodes

### Option 2: Keep for Comparison
If you want to compare old vs new performance:
- Keep `hybrid_render` (old renderer)
- Delete everything else

---

## After Cleanup: Minimal Network

You'll have just **9 essential nodes**:

```
mouse_input ──→ pollination_system ──→ structures_data ──→ gpu_renderer
                       ↑                  visitors_data         ↓
                 frame_timer              trails_data        OUTPUT
                       ↑                  particles_data
              hybrid_data_exporter
```

**That's it!** Clean, simple, optimized.

---

## Verification After Cleanup

Check that it still works:

1. **Is gpu_renderer cooking?**
   - Look at `/project1/gpu_renderer/OUT`
   - Should show trees, visitors, trails

2. **Are tables updating?**
   - Open `structures_data` - should have 6 rows
   - Open `visitors_data` - should have rows
   - Values should change when you move mouse

3. **Is timer running?**
   - `frame_timer` should be cycling
   - Check its "done" channel is pulsing

If all 3 are true, cleanup was successful!

---

## What Each Essential Node Does

| Node | Purpose | Can Delete? |
|------|---------|-------------|
| mouse_input | Captures input | NO - need input |
| scale_to_canvas | Scales to pixels | NO - need scaling |
| pollination_system | All behavior logic | NO - the brain |
| frame_timer | 60 FPS clock | NO - drives updates |
| frame_timer_callbacks1 | Calls exporter | NO - connects timer |
| hybrid_data_exporter | Writes to tables | NO - data bridge |
| structures_data | Tree positions | NO - data storage |
| visitors_data | Visitor positions | NO - data storage |
| trails_data | Trail points | NO - data storage |
| particles_data | Particle effects | NO - data storage |
| **gpu_renderer** | **Final output** | **NO - your output!** |

---

## Summary

**Before Cleanup:** ~25+ nodes (confusing!)
**After Cleanup:** 9-12 nodes (clear!)

**Active path:**
```
Input → Logic → Data → Renderer → Output
```

**Everything else was experimental scaffolding that can go.**
