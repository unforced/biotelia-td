# CLAUDE.md - Project Orientation Guide

## Current Status: Hybrid Python + TouchDesigner (Optimized & Production-Ready)

**Last Updated:** 2025-11-25
**Current Priority:** TouchDesigner file consolidated, ready for next steps

**Recent Changes:**
- ✅ TouchDesigner file moved to root directory (`biotelia-pollination.toe`)
- ✅ All work consolidated in `biotelia-td` directory
- ✅ Created comprehensive verification guide ([TD_VERIFICATION.md](TD_VERIFICATION.md))
- ✅ Ready for production use

---

## What We've Built

A working interactive pollination visualization system that runs inside TouchDesigner, currently implemented using Python integration. The system is **fully functional** and rendering successfully.

### Current Architecture

```
TouchDesigner Project (/project1)
├── Python Integration
│   ├── pollination_system (Python DAT)
│   │   └── Core logic: PollinationSystem from /core/system.py
│   └── python_path (Text DAT)
│       └── Points to: /Users/unforced/Symbols/Codes/biotelia-td
│
├── Input System
│   ├── mouse_input (Mouse In CHOP)
│   └── scale_to_canvas (Math CHOP) → scales to 1920x1080
│
└── Rendering
    ├── pollination_render (Script TOP) → 1920x1080 output
    └── pollination_render_callbacks (Python DAT) → numpy rendering
```

### What's Currently Rendering

- **Dark green background** (forest floor aesthetic)
- **5 colored structures** (trees/mushrooms) - static positions
- **3 autonomous pollinators** (bee, butterfly, moth) - always moving
- **Mycelial network** - connections between structures
- **Mouse cursor** - represents a human visitor
- **Trails** - colored paths following moving entities
- **Auras** - glowing colors around entities based on last touched tree

---

## Core Concept (The Heart of Biotelia)

### Static Entities: Trees/Structures
- Fixed positions on canvas
- Each has unique color identity
- Emit subtle glowing aura
- Connected by mycelial network

### Moving Entities: Humans & Robot Pollinators
- **Initial state:** No color/neutral
- **After touching tree:** Absorbs that tree's color into their aura
- **While moving:** Leave colored trail that gradually fades
- **On touching different tree:** Creates spiral particle effect (pollination dance)
- **Trail behavior:** Fades over time, dissipates naturally

### The Magic Moment
When a moving entity carrying Color A touches a tree with Color B:
→ Beautiful spiral particle effect
→ Visual representation of cross-pollination
→ Entity's aura transitions to Color B

---

## Current Implementation Details

### Project Structure
```
/Users/unforced/Symbols/Codes/biotelia-td/
├── biotelia-pollination.toe  # TouchDesigner project file ⭐
├── core/
│   ├── system.py       # Main PollinationSystem orchestrator
│   ├── aura.py         # VisitorAura - color absorption logic
│   ├── trail.py        # MovementTrail - fading trail particles
│   ├── dance.py        # PollinationDance - spiral effects
│   ├── agent.py        # AutonomousAgent - bees/butterflies/moths
│   ├── structure.py    # Structure - trees/mushrooms
│   └── mycelium.py     # MycelialNetwork - background connections
├── docs/               # Comprehensive documentation
│   ├── TD_VERIFICATION.md  # Setup verification checklist
│   ├── HYBRID_APPROACH.md  # Architecture explanation
│   └── OPTIMIZED_RENDERING.md # Performance details
├── config.py           # Colors, positions, parameters
├── standalone.py       # Standalone Pygame version (for testing)
└── run_animation_td.py # TD animation helper script
```

### TouchDesigner Flow
1. **Mouse In CHOP** captures position (0-1 normalized)
2. **Math CHOP** scales to canvas coordinates (1920x1080)
3. **Python DAT** (pollination_system) runs logic:
   - Parses visitor positions
   - Updates all systems (trails, auras, dances, agents)
   - Returns render data dictionary
4. **Script TOP** (pollination_render) renders using numpy:
   - Draws all layers to RGBA canvas
   - Outputs texture for projection

### Performance
- Running at 60 FPS
- CPU-based rendering (numpy array operations)
- ~0.033ms cook time per frame
- Resolution: 1920x1080

---

## Next Priority: Native TouchDesigner Implementation

### Why Consider This?

**Current Approach (Python):**
- ✓ Working and functional
- ✓ Easy to prototype and test
- ✗ CPU-based rendering (slower)
- ✗ Limited by Python DAT performance
- ✗ numpy array manipulation for every frame

**Potential Native TD Approach:**
- ✓ GPU-accelerated (TOPs/SOPs)
- ✓ Real-time performance at scale
- ✓ Native particle systems
- ✓ Better for multi-projector setups
- ✓ Cleaner data flow

### Proposed Native TD Architecture

```
Structure Setup (One-time)
└── Constant TOPs → 5 colored circles (trees)
    └── Composite → background layer

Moving Entities (Per frame)
├── CHOP → Position data
├── Instancing → Aura circles at positions
├── Trail TOP → Motion blur/fade effect
└── Particle SOP → Spiral effects on collision

Composition
└── Composite TOP → Layer all effects
    └── Output → Multi-projector mapping
```

### Key Components to Explore

1. **Static Trees:**
   - Circle TOP or Constant TOP with colored circles
   - Fixed positions, no updates needed
   - Maybe SOP geometry with glow shader

2. **Moving Entities:**
   - CHOP position data → Instance component
   - Each entity instance has color parameter
   - Circle TOP instances following CHOP positions

3. **Aura System:**
   - Blur TOP on entity positions
   - Color driven by "last touched tree" parameter
   - Composite with additive blending

4. **Trail System:**
   - Trail CHOP (records position history)
   - Render as instanced circles with alpha fade
   - OR use Trail TOP with feedback loop

5. **Collision Detection:**
   - Distance calculation in CHOP (entity pos - tree pos)
   - Trigger on threshold crossing
   - Fire Execute DAT → spawn particle system

6. **Spiral Particle Effect:**
   - Particle SOP with spiral motion
   - Spawned via Execute DAT on collision
   - Color blend between two sources
   - Lifetime fade

7. **Mycelial Network:**
   - Line SOP connecting tree positions
   - Animated particles along lines
   - Can use Lookup CHOP for flow animation

---

## Decision Point: Python vs Native TD

### Keep Python If:
- Performance is already sufficient
- Want to keep logic in version-controlled code
- Need to match existing p5.js prototype exactly
- Prefer readable imperative code

### Move to Native TD If:
- Need better performance (GPU acceleration)
- Want real-time scalability (more entities, higher res)
- Multi-projector setup requires more power
- Want to leverage TD's particle systems

### Hybrid Approach (Recommended to Explore First):
- Keep Python for logic (collision detection, state management)
- Use TOPs for rendering (GPU-accelerated)
- Python generates CHOP data → TOPs render
- Best of both worlds

---

## Immediate Next Steps

### Option A: Optimize Current Python Approach
1. Profile performance bottlenecks
2. Optimize numpy rendering
3. Add multi-projector output
4. Test with real mocap data

### Option B: Prototype Native TD Version
1. Create simple POC with one tree + one entity
2. Implement aura color transfer
3. Add trail effect
4. Test spiral particle effect on collision
5. Compare performance

### Option C: Hybrid Approach
1. Keep Python logic for state management
2. Export positions/colors to CHOPs
3. Render using TOPs (GPU)
4. Measure performance improvement

---

## Configuration & Parameters

All visual parameters in `config.py`:

```python
# Structure colors (trees)
STRUCTURE_COLORS = {
    'structure1': [255, 230, 100],  # Yellow
    'structure2': [255, 140, 180],  # Pink
    'structure3': [180, 120, 255],  # Purple
    'structure4': [100, 255, 180],  # Cyan
    'structure5': [255, 180, 100],  # Orange
}

# Aura behavior
AURA_DECAY_RATE = 0.998      # How long aura persists
AURA_GLOW_RADIUS = 18        # Size of glow

# Trail behavior
TRAIL_MAX_POINTS = 80        # Length of trail
TRAIL_FADE_RATE = 0.15       # How fast trail fades
TRAIL_POINT_SIZE = 6         # Size of trail particles
```

---

## Testing the Current System

### Quick Test
1. Open TouchDesigner project
2. Look at `pollination_render` Script TOP
3. Move mouse over TD window
4. Should see:
   - Mouse cursor as yellow dot
   - Colored structures
   - Moving pollinators
   - Trails following mouse when near structures

### Adding Real Mocap
Replace `mouse_input` with:
- OSC In CHOP (for motion capture systems)
- Configure channels as `person0_x`, `person0_y`, etc.
- Update Python DAT to parse multiple people

---

## Files Reference

### Active Files
- `biotelia-pollination.toe` - TouchDesigner project file ⭐
- `docs/CLAUDE.md` - This file (orientation)
- `docs/TD_VERIFICATION.md` - TD setup verification checklist
- `docs/HYBRID_APPROACH.md` - Architecture explanation
- `docs/OPTIMIZED_RENDERING.md` - Performance optimization details
- `docs/NETWORK_LAYOUT.md` - TD network organization
- `config.py` - All visual parameters
- `core/*.py` - Python system logic
- `README.md` - General project overview

### Quick Start
1. Open `biotelia-pollination.toe` in TouchDesigner
2. Follow [TD_VERIFICATION.md](TD_VERIFICATION.md) checklist
3. View output at `/project1/gpu_renderer/OUT`

---

## Questions to Answer Next

1. **Performance:** Is current Python approach fast enough for production?
2. **Scale:** How many simultaneous visitors do we need to support?
3. **Resolution:** Will we go beyond 1920x1080?
4. **Projectors:** How many projectors in final setup?
5. **Mocap:** What's the input format from motion capture system?

These answers will help decide between Python, native TD, or hybrid approach.

---

## Current State: WORKING ✓

The system is functional and rendering. The choice now is whether to optimize what we have or rebuild with native TouchDesigner components for better performance and scalability.

**Recommendation:** Start with a small native TD prototype (Option B) to compare approaches, while keeping the working Python version as reference.
