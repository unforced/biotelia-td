# TouchDesigner Integration Guide

Complete guide for integrating the Biotelia Pollination System into TouchDesigner.

## Quick Start

### Option 1: Simple Video Stream (Fastest)

1. Run standalone Python app: `python standalone.py`
2. Use **Spout** (Windows) or **Syphon** (Mac) to stream to TouchDesigner
3. In TD, add **Spout In TOP** or **Syphon In TOP**
4. Apply projection mapping

**Pros**: Immediate, no code changes  
**Cons**: Can't manipulate individual particles in TD

---

### Option 2: Python DAT Integration (Recommended)

Full integration with TouchDesigner's Python environment.

## Step-by-Step TouchDesigner Integration

### 1. Prepare Python Code

Copy the entire `biotelia-td` folder to a location TouchDesigner can access.

### 2. Create TouchDesigner Network

```
┌──────────────┐
│  CHOP In     │ ← Mocap position data
└──────┬───────┘
       │
┌──────▼───────┐
│ Python DAT   │ ← Main logic (see below)
│ "pollination"│
└──────┬───────┘
       │
┌──────▼───────┐
│ Script TOP   │ ← Render output
│              │
└──────┬───────┘
       │
┌──────▼───────┐
│ Projection   │ → Multi-projector mapping
└──────────────┘
```

### 3. Python DAT Setup

Create a Python DAT called `pollination_system`:

```python
"""
Biotelia Pollination System - TouchDesigner Integration
Place this code in a Python DAT
"""

import sys
import os

# Add biotelia-td to path (adjust path as needed)
biotelia_path = '/path/to/biotelia-td'
if biotelia_path not in sys.path:
    sys.path.insert(0, biotelia_path)

from core import PollinationSystem
import config
import numpy as np

# Global system instance
system = None
initialized = False

def initialize():
    """Initialize the pollination system (call once)."""
    global system, initialized
    
    if initialized:
        return
    
    # Create system
    system = PollinationSystem(
        canvas_width=1920,
        canvas_height=1080,
        structures_config=config.STRUCTURES
    )
    
    # Add autonomous agents
    system.add_autonomous_agent('bee')
    system.add_autonomous_agent('butterfly')
    system.add_autonomous_agent('moth')
    
    initialized = True
    print("✓ Biotelia Pollination System initialized")

def update_frame(chop_data, frame_data):
    """
    Update pollination system each frame.
    
    Args:
        chop_data: CHOP channels with position data
        frame_data: Frame info from TD
        
    Returns:
        Render data dictionary
    """
    global system
    
    if not initialized:
        initialize()
    
    # Parse visitor positions from CHOP
    visitors = []
    num_people = 6  # Adjust based on your mocap setup
    
    for i in range(num_people):
        x_channel = f'person{i}_x'
        y_channel = f'person{i}_y'
        
        if x_channel in chop_data and y_channel in chop_data:
            visitors.append({
                'id': i,
                'x': chop_data[x_channel],
                'y': chop_data[y_channel],
            })
    
    # Calculate dt from frame time
    dt = 1.0 / 60.0  # Or use frame_data.time
    
    # Update system
    render_data = system.update(visitors, dt)
    
    return render_data

# Auto-initialize on load
initialize()
```

### 4. CHOP Input Format

Your mocap CHOP should have channels:

```
person0_x
person0_y
person1_x
person1_y
person2_x
person2_y
...
```

**Example CHOP network:**

```
┌─────────────┐
│ OSC In CHOP │ ← Mocap data via OSC
└──────┬──────┘
       │
┌──────▼──────┐
│ Select CHOP │ ← Extract position channels
└──────┬──────┘
       │
┌──────▼──────┐
│ Math CHOP   │ ← Scale to canvas coordinates
└──────┬──────┘
       │
       └─→ Python DAT
```

### 5. Script TOP Rendering

Create a Script TOP that calls the Python DAT:

```python
"""
Script TOP - Renders pollination system output
"""

import numpy as np

def onCook(scriptOp):
    # Get render data from Python DAT
    pollination_dat = op('pollination_system')
    render_data = pollination_dat.module.update_frame(
        op('mocap_chop'),  # Your CHOP with position data
        scriptOp.time
    )
    
    # Create output texture
    width = 1920
    height = 1080
    
    # Initialize black canvas
    scriptOp.copyNumpyArray(np.zeros((height, width, 4), dtype=np.float32))
    
    # TODO: Render each layer
    # (See detailed rendering section below)
```

---

## Detailed Rendering in TouchDesigner

### Method A: Script TOP (CPU Rendering)

Render directly in Python (similar to Pygame):

```python
def render_to_numpy(render_data, width, height):
    """Render all layers to numpy array."""
    
    # Create RGBA canvas
    canvas = np.zeros((height, width, 4), dtype=np.float32)
    
    # Render mycelium
    for connection in render_data['mycelium']:
        # Draw lines using numpy operations
        pass
    
    # Render trails
    for trail in render_data['visitor_trails']:
        for point in trail:
            draw_circle(canvas, point['x'], point['y'], point['size'], point['color'], point['alpha'])
    
    # ... render other layers
    
    return canvas
```

### Method B: TOP Composition (GPU Rendering - Recommended)

Use TouchDesigner's built-in TOPs for better performance:

```
1. Python DAT outputs particle positions/colors
2. CHOP outputs positions as channels
3. Use Circle TOP / Constant TOP for each element
4. Composite layers together
```

**Example for trails:**

```python
# In Python DAT, export trail data to CHOP
def get_trail_chop_data(render_data):
    """Convert trail data to CHOP channels."""
    
    channels = {}
    point_index = 0
    
    for trail in render_data['visitor_trails']:
        for point in trail:
            channels[f'trail{point_index}_x'] = point['x']
            channels[f'trail{point_index}_y'] = point['y']
            channels[f'trail{point_index}_r'] = point['color'][0] / 255.0
            channels[f'trail{point_index}_g'] = point['color'][1] / 255.0
            channels[f'trail{point_index}_b'] = point['color'][2] / 255.0
            channels[f'trail{point_index}_a'] = point['alpha']
            point_index += 1
    
    return channels
```

Then use **Instancing** to draw all trail points at once.

---

## Example TD Network (Detailed)

```
Mocap Input:
┌─────────────┐
│ OSC In CHOP │ port 9000
└──────┬──────┘
       │
┌──────▼──────┐
│ Select CHOP │ select position channels
└──────┬──────┘
       │
┌──────▼──────┐
│ Math CHOP   │ scale 0-1 → 0-1920/1080
└──────┬──────┘
       │
       ├─→ Python DAT "pollination_system"
       │
       └─→ Info CHOP (for debugging)

Rendering:
┌─────────────────┐
│ Python DAT      │ pollination_system
└────────┬────────┘
         │
         ├─→ Execute DAT (exports to CHOPs)
         │
┌────────▼────────┐
│ Multiple CHOPs  │ trail_data, aura_data, etc.
└────────┬────────┘
         │
┌────────▼────────┐
│ Circle TOPs     │ render circles using instancing
└────────┬────────┘
         │
┌────────▼────────┐
│ Composite TOP   │ blend all layers
└────────┬────────┘
         │
┌────────▼────────┐
│ Projection TOPs │ mapping, warping, edge blend
└─────────────────┘
```

---

## OSC Input Example

If your mocap sends OSC data:

```python
# OSC message format
/person/0/position x y
/person/1/position x y
```

**OSC In CHOP settings:**
- Protocol: UDP
- Port: 9000
- Network Address: `/person/*/position`

---

## Performance Tips

1. **Limit particle count**: Cap trail points to ~80 per person
2. **Use GPU rendering**: Prefer TOPs over Script TOP when possible
3. **Update rate**: Run Python logic at 30-60 FPS max
4. **Caching**: Cache structure positions (don't recalculate)
5. **Instancing**: Use geometry instancing for repeated elements

---

## Multi-Projector Setup

TouchDesigner excels at multi-projector setups:

1. **Create output TOPs** for each projector
2. **Use Stoner TOP** for warping/keystoning
3. **Use Edge Blend TOP** between projectors
4. **Use Multi-Output Window** for spanning displays

**Example 3-projector setup:**

```
┌─────────────┐
│ Main Canvas │ 5760x1080 (3 × 1920x1080)
└──────┬──────┘
       │
   ┌───┼───┐
   │   │   │
┌──▼───▼───▼──┐
│ Proj1 Proj2 Proj3
│ Stoner TOPs
└──┬───┬───┬──┘
   │   │   │
   └───┼───┘
       │
┌──────▼──────┐
│ Edge Blend  │
└─────────────┘
```

---

## Troubleshooting

### Python DAT errors

Check Python path:
```python
import sys
print(sys.path)
```

### No render output

- Verify CHOP has position data
- Check Python DAT is running (`initialized = True`)
- Print render_data to textport

### Performance lag

- Lower update rate (30 FPS instead of 60)
- Reduce trail points
- Use GPU rendering (TOPs) instead of CPU

---

## Next Steps

1. **Test with simulated mocap** using Mouse In CHOP
2. **Connect real mocap** via OSC or CHOP
3. **Build rendering network** using TOPs
4. **Calibrate projection mapping**
5. **Add edge blending** for multi-projector

---

## Resources

- **TouchDesigner Forum**: https://forum.derivative.ca
- **OSC Protocol**: For mocap integration
- **Spout/Syphon**: For external apps
- **Python in TD**: https://docs.derivative.ca/Python

---

**Ready to integrate!** Start with Method A (Script TOP) for quick testing, then migrate to Method B (TOP composition) for production performance.
