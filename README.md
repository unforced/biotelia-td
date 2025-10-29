# Biotelia Pollination System - Python/TouchDesigner Version

Interactive floor projection visualization showing visitors as pollinators in a living ecosystem.

## Features

- **Single-color bioluminescence** - Visitors glow with the color of the last tree they touched
- **Movement trails** - Colored trails follow visitors, spreading their bioluminescence
- **Pollination swirls** - Beautiful spiral effects when different colors meet
- **Autonomous pollinators** - Bees, butterflies, and moths with their own bioluminescence
- **Mycelial network** - Always-present connections showing ecosystem is already alive
- **Multi-projector ready** - Designed for TouchDesigner projection mapping

## Quick Start (Standalone Preview)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Standalone Preview

```bash
python standalone.py
```

### 3. Controls

- **Mouse**: Click and drag people around
- **0-8**: Set number of people
- **+/-**: Adjust intensity
- **SPACE**: Pause/unpause
- **S**: Save screenshot
- **ESC/Q**: Quit

## Project Structure

```
biotelia-td/
├── core/               # Core logic classes
│   ├── aura.py        # VisitorAura - bioluminescence
│   ├── trail.py       # MovementTrail - colored trails
│   ├── dance.py       # PollinationDance - swirl effects
│   ├── agent.py       # AutonomousAgent - bees/butterflies/moths
│   ├── structure.py   # Structure - trees/mushrooms
│   ├── mycelium.py    # MycelialNetwork - connections
│   └── system.py      # PollinationSystem - main orchestrator
├── render/            # Rendering modules
│   └── pygame_renderer.py  # Pygame-based renderer
├── input/             # Input handling
│   └── simulator.py   # Mocap simulator for testing
├── config.py          # Colors, settings, structure positions
├── standalone.py      # Standalone preview application
└── README.md          # This file
```

## TouchDesigner Integration

### Input Format

The system expects position data as a list of dictionaries:

```python
visitors = [
    {"id": 0, "x": 512, "y": 384},
    {"id": 1, "x": 720, "y": 200},
]

pollinators = [
    {"id": 0, "x": 300, "y": 400, "type": "bee"},
    {"id": 1, "x": 600, "y": 500, "type": "butterfly"},
]
```

### Basic TouchDesigner Integration

1. **Import Python code into TD Python DAT**
2. **Create CHOP with position data** (columns: `person0_x, person0_y, person1_x, person1_y...`)
3. **Call system.update()** with position list
4. **Render output** to Script TOP or texture

### Example TD Python DAT

```python
import sys
sys.path.append('/path/to/biotelia-td')

from core import PollinationSystem
import config

# Initialize (run once)
system = PollinationSystem(1920, 1080, config.STRUCTURES)
system.add_autonomous_agent('bee')
system.add_autonomous_agent('butterfly')

# Update (called each frame)
def update_frame(chop_data):
    # Parse CHOP data into position list
    visitors = []
    for i in range(num_people):
        visitors.append({
            'id': i,
            'x': chop_data[f'person{i}_x'],
            'y': chop_data[f'person{i}_y'],
        })
    
    # Update system
    render_data = system.update(visitors)
    
    # Pass render_data to rendering TOPs
    return render_data
```

## Configuration

Edit `config.py` to customize:

- Structure positions and colors
- Pollinator colors and behavior
- Aura decay rates
- Trail lengths and fade rates
- Canvas dimensions

### Structure Positions

Positions are normalized (0-1) and scaled to canvas size:

```python
STRUCTURES = [
    {'id': 0, 'x': 0.20, 'y': 0.30, 'radius': 80, 'color': [255, 230, 100]},
    # ... more structures
]
```

### Adjusting Bioluminescence Duration

In `config.py`:

```python
AURA_DECAY_RATE = 0.998  # Lower = longer lasting (0.998 = very slow)
```

## Architecture

### Data Flow

```
Mocap Positions → PollinationSystem.update() → Render Data → Renderer
```

### Core Classes

- **PollinationSystem**: Main orchestrator
- **VisitorAura**: Manages single-color glow around visitors
- **MovementTrail**: Tracks colored trail behind moving visitors
- **PollinationDance**: Creates swirl when colors meet
- **AutonomousAgent**: Independent pollinator (bee/butterfly/moth)
- **Structure**: Tree or mushroom that visitors pollinate
- **MycelialNetwork**: Background connections between structures

### Rendering

The system produces render data as dictionaries describing visual elements:

```python
render_data = {
    'mycelium': [...],        # Network lines and particles
    'structures': [...],      # Trees/mushrooms
    'visitor_auras': [...],   # Bioluminescent glows
    'visitor_trails': [...],  # Movement trails
    'dances': [...],          # Pollination swirls
    'agents': [...],          # Bees/butterflies/moths
    'visitors': [...],        # Person position indicators
}
```

Renderers interpret this data to draw the visualization.

## Performance

- **60 FPS** target frame rate
- **~100-200 particles** total at peak (trails + swirls + mycelium)
- **Efficient for 3-6 visitors + 3 autonomous agents**
- **Python NumPy** for fast array operations

## Development Workflow

### Testing Visuals

```bash
python standalone.py
```

Use mouse to drag people around and test interactions.

### Adding New Pollinator Types

Edit `core/agent.py` and `config.py`:

```python
# In config.py
AGENT_SETTINGS = {
    'dragonfly': {
        'speed': 70,
        'size': 5,
        'wiggle': 2.0,
        'color': np.array([100, 200, 255], dtype=np.uint8),
    },
}

# In standalone.py or TD
system.add_autonomous_agent('dragonfly')
```

### Adjusting Colors

All colors in `config.py` as NumPy arrays:

```python
STRUCTURE_COLORS = {
    'structure1': np.array([255, 230, 100], dtype=np.uint8),  # RGB 0-255
}
```

## Troubleshooting

### "No module named 'pygame'"

```bash
pip install pygame
```

### "No module named 'numpy'"

```bash
pip install numpy
```

### Performance Issues

- Reduce `TRAIL_MAX_POINTS` in config.py
- Reduce number of autonomous agents
- Lower `TARGET_FPS`

### Trails Not Appearing

- Visitors must touch a structure first to get a color
- Check that `AURA_DECAY_RATE` isn't too high (try 0.998)

## Future Enhancements

- [ ] TouchDesigner native rendering (TOPs)
- [ ] OSC input for mocap data
- [ ] Multi-projector calibration tools
- [ ] Physical computing integration (LED sync)
- [ ] Recording/playback of sessions

## Credits

**Concept**: Biotelia pollination ecosystem  
**Implementation**: Python port from p5.js prototype  
**Framework**: NumPy, Pygame, TouchDesigner-ready

## License

Created for the Biotelia installation project.

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-29  
**Status**: Production Ready 🌸
