# Hybrid Approach: Python Logic + TD Rendering

**Created:** 2025-01-14
**Status:** ✓ Implemented and working

## What We Built

A **clean hybrid architecture** that combines Python's flexibility for logic with TouchDesigner's potential for GPU rendering.

### Architecture

```
Mouse Input (CHOP)
    ↓
Python PollinationSystem (all logic)
    ↓
Table DATs (structured data)
    ├─ structures_data
    ├─ visitors_data
    ├─ trails_data
    └─ particles_data
    ↓
hybrid_render (Script TOP) → 1920x1080 output
```

## Key Components

### 1. Data Export (`/project1/hybrid_data_exporter`)
- Python DAT that exports structured data
- Called by timer every frame (60 FPS)
- Writes to table DATs with columns: `id, tx, ty, r, g, b, radius, alpha`

### 2. Table DATs (Data Storage)
- **structures_data**: Trees/mushrooms (5 items)
- **visitors_data**: Humans + autonomous agents
- **trails_data**: Movement trail points
- **particles_data**: Spiral pollination effects

### 3. Renderer (`/project1/hybrid_render`)
- Script TOP (1920x1080)
- Reads from table DATs
- Renders circles using numpy (for now)

### 4. Timer (`/project1/frame_timer`)
- Cycles every frame
- Triggers data export via callbacks

## Benefits vs Original Approach

### Original (Pure Python Rendering)
```
Python Logic → Inline Pixel Drawing → Script TOP
```
- ❌ Rendering mixed with logic
- ❌ Hard to debug
- ❌ Scaling requires code changes

### Hybrid (Current)
```
Python Logic → Structured Data → Rendering
```
- ✓ Clean separation of concerns
- ✓ Easy to inspect data (look at tables)
- ✓ Scalable (more trees = more rows, not more nodes)
- ✓ Can swap rendering approach without changing logic

### Future (Native TD Rendering)
```
Python Logic → Table DATs → Instance TOPs (GPU) → Composite
```
- ✓ Same data format
- ✓ GPU-accelerated rendering
- ✓ Just replace hybrid_render with native TD network

## How It Solves Your Concerns

### Problem: "One TD node per entity doesn't scale"
**Solution:** All entities of same type in one table
- 5 trees = 5 rows in structures_data
- N visitors = N rows in visitors_data
- No manual node creation

### Problem: "Native TD felt messy and buggy"
**Solution:** Python handles all complexity
- Collision detection: Python
- State management: Python
- Color transfer logic: Python
- TD just renders the output data

### Problem: "Easier to understand/modify"
**Solution:** Inspect data tables
- See exact x, y, color values in real-time
- Debug without reading render code
- Modify by changing table format

## Current Status

### Working Now
- ✓ Frame timer updates at 60 FPS
- ✓ Python logic runs (all features)
- ✓ Data exports to tables
- ✓ Rendering produces 1920x1080 output

### Still Numpy Rendering
- Uses numpy pixel loops (same as original)
- **But**: Now reads structured data, not mixed with logic
- **Next step**: Can swap for native TD rendering without changing data export

## Next Steps (Optional)

### Option A: Keep It As-Is
- Works now
- Profile to see if performance is sufficient
- If fast enough, ship it!

### Option B: Native TD Rendering
Replace `hybrid_render` with:
1. **Circle TOP** (one instance)
2. **Instance component** (reads tx, ty, r, g, b from tables)
3. **Composite TOP** (layers everything)

This would give GPU rendering while keeping all the Python logic.

### Option C: Optimize Numpy
- Vectorize circle drawing
- Use scipy/skimage for faster rendering
- Still CPU but faster

## Files Modified

- `/project1/hybrid_data_exporter` - Exports to tables
- `/project1/hybrid_render` - Renders from tables
- `/project1/hybrid_render_callbacks1` - Rendering code
- `/project1/frame_timer` - 60 FPS timer
- `/project1/frame_timer_callbacks1` - Calls exporter
- `/project1/structures_data` - Structure data table
- `/project1/visitors_data` - Visitor/agent data table
- `/project1/trails_data` - Trail points table
- `/project1/particles_data` - Particle data table

## Usage

### View Output
- Look at `/project1/hybrid_render` TOP
- Should show trees, visitors, trails at 1920x1080

### Debug Data
- Open any `*_data` table DAT
- See live values updating

### Modify Behavior
- Edit `/project1/pollination_system` for logic changes
- Edit `/project1/hybrid_data_exporter` for data format changes
- Edit `/project1/hybrid_render_callbacks1` for rendering changes

## Performance

**Current:** ~Same as original (numpy rendering)
**Bottleneck:** CPU pixel loops in render callbacks
**Solution:** Native TD TOPs would move to GPU

## Summary

You now have a **clean, scalable architecture** that:
1. Keeps Python logic readable and flexible
2. Separates data from rendering
3. Makes debugging easy (inspect tables)
4. Doesn't require manual node duplication
5. Can be upgraded to GPU rendering without changing logic

**The messy "one node per tree" problem is solved.**
