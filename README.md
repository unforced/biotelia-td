# Biotelia Pollination System

Interactive floor projection where visitors become pollinators in a living ecosystem.

**Status:** ✅ Production Ready | **Resolution:** 1920×2160 | **Input:** Mocap/OSC

---

## Quick Start

### Production Deployment

```bash
# Clone repository
git clone https://github.com/unforced/biotelia-td.git
cd biotelia-td

# Open TouchDesigner
# File: biotelia-pollination.toe
```

**Configure:**
1. `/project1/settings_control` → **Resmode:** Production, **Inputmode:** Mocap
2. `/project1/mocap` → Verify coordinate mapping settings
3. Check output at `/project1/gpu_renderer/OUT`

**📖 See [PRODUCTION_HANDOFF.md](PRODUCTION_HANDOFF.md) for complete setup guide**

---

## The Experience

Visitors become pollinators in an interactive ecosystem:

- **Touch a structure** (glowing tree) → Absorb its color into your aura
- **Move through space** → Leave colored trails that fade over time
- **Touch different structure** → Create spiral pollination dance effect
- **Visual metaphor** → Cross-pollination between different colored trees

---

## Documentation

**For Production:**
- **[PRODUCTION_HANDOFF.md](PRODUCTION_HANDOFF.md)** - Complete production setup
- **[MOCAP_SETUP.md](MOCAP_SETUP.md)** - Mocap integration details
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Moving to new machines

**For Development:**
- **[CLAUDE.md](CLAUDE.md)** - AI assistant orientation guide
- **[config.py](config.py)** - Visual parameters & settings

**Archive:**
- [docs/](docs/) - Historical documentation and development notes

---

## Current Configuration

**Physical Setup:**
- Room: 20 ft × 30 ft
- Projection area: 7 ft × 8 ft (centered)
- Mocap tracking: Up to 9 visitors
- Mocap range: -1 to 1 (center = 0, 0)

**Technical:**
- Resolution: 1920 × 2160 pixels (portrait 8:9 aspect)
- Frame rate: 60 FPS
- Input: OSC on port 55556 (channels: p0x, p0y, p1x, p1y ... p8x, p8y)
- Coordinate mapping: Pre-configured for room layout

**Visual Elements:**
- 3 colored structures (trees) at fixed positions
- Visitor auras (absorb color from structures)
- Flowing watery trails with fade effect
- Spiral pollination dances (on color change)

---

## Architecture

### Stack

```
Mocap System → OSC → TouchDesigner → Projector
                         ↓
                   Python Logic
                   (core/*.py)
                         ↓
                   GPU Rendering
                   (1920×2160)
```

### TouchDesigner Network

**14 essential nodes organized in 4 rows:**

- **Input & Settings:** mocap, settings_control, input_switch
- **Core System:** pollination_system (Python), gpu_renderer (output)
- **Timing:** frame_timer, frame_speed, animation_driver
- **Utilities:** mcp_webserver_base, python_path

### Python Modules

```
core/
├── system.py       # PollinationSystem orchestrator
├── aura.py         # Visitor aura (color absorption)
├── trail.py        # Movement trails (fading)
├── dance.py        # Pollination dances (spiral effects)
├── structure.py    # Trees/structures
└── agent.py        # Autonomous agents (disabled in production)
```

---

## File Structure

```
biotelia-td/
├── biotelia-pollination.toe         # TouchDesigner project ⭐
├── config.py                         # Visual parameters
├── pollination_system_current.py    # System logic
├── improved_rendering.py             # Rendering with effects
├── core/                             # Python modules
├── docs/                             # Documentation
├── PRODUCTION_HANDOFF.md             # Production setup ⭐
├── CLAUDE.md                         # AI assistant guide ⭐
├── DEPLOYMENT.md                     # Deployment guide
├── MOCAP_SETUP.md                    # Mocap integration
└── README.md                         # This file
```

---

## Key Features

### Coordinate Mapping System

Tunable parameters in `/project1/mocap` for mapping mocap coordinates to canvas:

- **X/Y Scale** - Multiply mocap values
- **X/Y Offset** - Shift coordinates
- **Input Range** - Toggle between 0-1 or -1 to 1

**Pre-configured for:** 7×8 ft projection centered in 20×30 ft room

### Settings UI

Control panel at `/project1/settings_control`:

- **Resmode** - Test (1138×1280) or Production (1920×2160)
- **Inputmode** - Mouse/Test or Mocap/OSC

**No Python code editing needed on production machine!**

### Dynamic Path Resolution

System automatically finds project files using `project.folder`:
- Works on any machine/username
- No hardcoded paths
- Fails fast with clear errors

---

## Performance

**Current:**
- 60 FPS at 1920×2160
- Up to 9 simultaneous visitors
- Real-time coordinate mapping
- Watery flowing trail effects

**Optimizations:**
- Vectorized numpy rendering (10-100x faster than original)
- GPU-accelerated composition
- Efficient trail fade algorithm
- Additive blending for glows

---

## Configuration

### Visual Parameters (`config.py`)

```python
# Structures (trees)
STRUCTURES = [
    {'name': 'structure1', 'x': 0.3, 'y': 0.25, 'color': [255, 230, 100]},  # Yellow
    {'name': 'structure2', 'x': 0.7, 'y': 0.25, 'color': [255, 140, 180]},  # Pink
    {'name': 'structure3', 'x': 0.5, 'y': 0.75, 'color': [180, 120, 255]},  # Purple
]

# Trail behavior
TRAIL_MAX_POINTS = 80        # Trail length
TRAIL_FADE_RATE = 0.15       # Fade speed
TRAIL_MIN_DISTANCE = 8       # Distance between points

# Aura behavior
AURA_DECAY_RATE = 0.998      # Persistence
AURA_GLOW_RADIUS = 18        # Size
```

**Note:** Positions use normalized 0-1 coordinates (scales to any resolution)

### Mocap Coordinate Mapping

Current settings for 7×8 ft centered projection:

```
X Scale:  2742.86
X Offset: 960
Y Scale:  4050
Y Offset: 1080
Input Range: -1 to 1
```

**Adjustable in TouchDesigner UI** - no code changes needed!

---

## Production Checklist

Before going live:

### Hardware
- [ ] TouchDesigner Commercial license
- [ ] Mocap system sending OSC to port 55556
- [ ] Projector configured for 1920×2160

### TouchDesigner
- [ ] Settings: Resmode = Production, Inputmode = Mocap
- [ ] Textport shows: "PRODUCTION mode" and "0 agents"
- [ ] OSC channels visible: p0x, p0y, p1x, p1y, etc.

### Testing
- [ ] Move in space → See position change
- [ ] Touch structure → Aura changes color
- [ ] Move → Trails appear
- [ ] Touch different structure → Pollination dance

**📖 See [PRODUCTION_HANDOFF.md](PRODUCTION_HANDOFF.md) for complete checklist**

---

## Troubleshooting

### No Visitors Appearing
- Check OSC data arriving at `/project1/mocap/oscin1`
- Verify Inputmode = "Mocap/OSC"
- Check people are inside projection area (7×8 ft centered zone)

### Wrong Positions
- Verify mocap range (-1 to 1 or 0 to 1?)
- Adjust coordinate mapping in `/project1/mocap`
- Test with person at known position

### Import Errors
- Ensure `.toe` file saved to disk in biotelia-td folder
- Check all files (core/, config.py) present
- See [DEPLOYMENT.md](DEPLOYMENT.md)

---

## Development

### Adding Structures

Edit `config.py`:

```python
STRUCTURES.append({
    'name': 'structure4',
    'x': 0.5,        # 0-1 normalized (0.5 = center)
    'y': 0.5,
    'color': [100, 255, 180]  # RGB
})
```

### Adjusting Visual Effects

Edit `config.py`:
- Trail length: `TRAIL_MAX_POINTS`
- Trail fade: `TRAIL_FADE_RATE`
- Aura size: `AURA_GLOW_RADIUS`
- Aura persistence: `AURA_DECAY_RATE`

### Module Reloading

If Python changes without restarting TD:

```python
# In TouchDesigner textport:
import sys
for mod in list(sys.modules.keys()):
    if 'core' in mod or 'pollination' in mod:
        del sys.modules[mod]

op('/project1/pollination_system').module.initialized = False
op('/project1/pollination_system').cook(force=True)
```

---

## Git Workflow

```bash
# Pull latest changes
git pull

# Changes embedded in .toe file
# Close and reopen TouchDesigner to see updates
```

---

## Support

**Repository:** https://github.com/unforced/biotelia-td

**Documentation:**
- Production setup: [PRODUCTION_HANDOFF.md](PRODUCTION_HANDOFF.md)
- AI assistant guide: [CLAUDE.md](CLAUDE.md)
- Deployment: [DEPLOYMENT.md](DEPLOYMENT.md)
- Mocap: [MOCAP_SETUP.md](MOCAP_SETUP.md)

**Contact:** Check git commit history for development log

---

**Status:** ✅ Production Ready
**Last Updated:** 2025-11-25
**Deployment:** 7×8 ft projection in 20×30 ft room
