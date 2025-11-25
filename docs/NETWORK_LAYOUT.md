# TouchDesigner Network Layout Guide

**Organization:** Left → Right data flow
**Updated:** 2025-01-14

---

## Main Network (/project1)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  LEFT              MIDDLE-LEFT        MIDDLE         RIGHT              │
│  (Input)           (Logic)            (Data)         (Renderers)        │
│                                                                         │
│  mouse_input ───→  pollination_system → structures  → gpu_renderer ⭐  │
│      │                    │              visitors       (OPTIMIZED)     │
│  scale_to_                │              trails                         │
│  _canvas                  │              particles    hybrid_render     │
│                           │                             (old/backup)    │
│                   frame_timer                                           │
│                      │                                                  │
│                   hybrid_data                                           │
│                   _exporter                                             │
│                                                                         │
│  TOP: mcp_webserver_base (utility)                                     │
│  BOTTOM: native_prototype (old, can ignore)                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Layer Breakdown

#### 🟢 INPUT (X: 0)
- **mouse_input** - Mouse position capture
- **scale_to_canvas** - Scales to 1920x1080
- **mcp_webserver_base** (top) - MCP server for remote control

#### 🟡 PYTHON LOGIC (X: 300)
- **python_path** - Path to biotelia-td folder
- **setup_python_path** - Initialize Python imports
- **pollination_system** - Core Python logic (main brain)
- **frame_timer** - 60 FPS update timer
- **frame_timer_callbacks1** - Timer callback script
- **hybrid_data_exporter** - Exports logic to data tables

#### 🔵 DATA TABLES (X: 600)
- **structures_data** - Trees (5 items)
- **visitors_data** - Humans + agents
- **trails_data** - Movement trails
- **particles_data** - Spiral effects

#### 🔴 RENDERERS (X: 900)
- **gpu_renderer** ⭐ - OPTIMIZED (use this!)
- **hybrid_render** - Original (backup/reference)
- **hybrid_render_callbacks1** - Old render code

#### ⚪ UNUSED/OLD (various positions)
- **structures_chop** (X: 750) - Not used anymore
- **visitors_chop** (X: 750) - Not used anymore
- **trails_chop** (X: 750) - Not used anymore
- **particles_chop** (X: 750) - Not used anymore
- **native_prototype** (X: 300, Y: -600) - Old prototype, can ignore

---

## Inside gpu_renderer (OPTIMIZED RENDERER)

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│  background ────┐                                    │
│                 ├──→ composite ──→ OUT ⭐           │
│  optimized_     │                                    │
│  circles ───────┘                                    │
│      │                                               │
│  optimized_circles_callbacks1                        │
│  (vectorized render code)                            │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Components
- **background** - Dark green constant (1920x1080)
- **optimized_circles** - Vectorized circle renderer (Script TOP)
- **optimized_circles_callbacks1** - Fast rendering code
- **composite** - GPU blend background + circles
- **OUT** - Final 1920x1080 output ⭐

---

## Data Flow Diagram

```
┌─────────────┐
│   Mouse     │
└──────┬──────┘
       │
       v
┌─────────────────┐
│ Python Logic    │  ← Runs every frame (60 FPS)
│ (all behavior)  │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Table DATs     │  ← Structured data
│  (easy to view) │     • structures
└────────┬────────┘     • visitors
         │              • trails
         │              • particles
         v
┌─────────────────┐
│ GPU Renderer    │  ← Vectorized numpy
│ (optimized)     │     10-100x faster
└────────┬────────┘
         │
         v
┌─────────────────┐
│   OUTPUT        │  ← 1920x1080
│ /gpu_renderer/  │     60 FPS
│      OUT        │
└─────────────────┘
```

---

## Quick Reference: What to Look At

### To Debug Logic
👉 **`/project1/pollination_system`** - Core Python behavior

### To Debug Data
👉 **`/project1/structures_data`** - See tree positions/colors
👉 **`/project1/visitors_data`** - See visitor/agent data
👉 **`/project1/trails_data`** - See trail points
👉 **`/project1/particles_data`** - See particle effects

### To See Output
👉 **`/project1/gpu_renderer/OUT`** ⭐ - Your final output (optimized)

### To Compare Performance
- **Old:** `/project1/hybrid_render`
- **New:** `/project1/gpu_renderer/OUT`

### To Modify Rendering
👉 **`/project1/gpu_renderer/optimized_circles_callbacks1`** - Render code

---

## Node Coordinates Reference

### Main Network Positions

| Node | X | Y | Purpose |
|------|---|---|---------|
| mouse_input | 0 | 0 | Input capture |
| scale_to_canvas | 0 | -100 | Scale to pixels |
| python_path | 300 | 200 | Python setup |
| pollination_system | 300 | 0 | Core logic |
| frame_timer | 300 | -200 | 60 FPS clock |
| hybrid_data_exporter | 300 | -400 | Export data |
| structures_data | 600 | 100 | Tree data |
| visitors_data | 600 | 0 | Visitor data |
| trails_data | 600 | -100 | Trail data |
| particles_data | 600 | -200 | Particle data |
| **gpu_renderer** ⭐ | **900** | **-100** | **Optimized output** |
| hybrid_render | 900 | 200 | Old renderer |

### GPU Renderer Internal

| Node | X | Y | Purpose |
|------|---|---|---------|
| background | 0 | 0 | Dark green BG |
| optimized_circles | 0 | -150 | Circle renderer |
| composite | 300 | -75 | Blend layers |
| **OUT** ⭐ | **500** | **-75** | **Final output** |

---

## Tips for Debugging

### 1. Check Data Flow
Look at tables in order:
1. Is `structures_data` populated? (should have 6 rows)
2. Is `visitors_data` populated? (varies with agents)
3. Is `trails_data` populated? (when moving)
4. Is `particles_data` populated? (when pollinating)

### 2. Check Logic
- Is `frame_timer` running? (should cycle continuously)
- Is `pollination_system` cooking? (check cook time)

### 3. Check Output
- Is `gpu_renderer/OUT` rendering? (should show scene)
- Compare with `hybrid_render` (should look identical, just faster)

### 4. Check Performance
```python
# In TextPort or Execute DAT
renderer = op('/project1/gpu_renderer/optimized_circles')
print(f"Cook time: {renderer.cookTime}ms")
# Should be < 2ms for full scene
```

---

## Clean Up (Optional)

### Can Safely Delete
- `/project1/structures_chop` - Not used
- `/project1/visitors_chop` - Not used
- `/project1/trails_chop` - Not used
- `/project1/particles_chop` - Not used
- `/project1/native_prototype` - Old prototype
- `/project1/hybrid_renderer` - Old component (inside hybrid_renderer base)

### Keep for Reference
- `/project1/hybrid_render` - Original renderer (compare performance)
- `/project1/pollination_render` - Even older (if it exists)

---

## Summary

**Primary Output:** `/project1/gpu_renderer/OUT` ⭐

**Organized Layout:**
- **Left:** Input
- **Middle-Left:** Python logic + timer
- **Middle:** Data tables (easy to inspect!)
- **Right:** Renderers (optimized + old)

**Easy Debugging:**
- Logic problem? → Check `/project1/pollination_system`
- Data problem? → Check `*_data` tables
- Render problem? → Check `/project1/gpu_renderer/optimized_circles_callbacks1`
- Output problem? → Look at `/project1/gpu_renderer/OUT`

**Flow is clean:** Input → Logic → Data → Render → Output
