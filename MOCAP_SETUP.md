# Mocap Integration Setup Guide

## Overview

The system supports both test mode (mouse + autonomous agents) and production mode (9 mocap-tracked visitors).

## Visitor Configuration

**Total Visitors:** 9
- 3 robot pollinators (mocap-tracked)
- 6 human visitors (mocap-tracked)

**Behind the scenes:** All 9 are treated identically - they all create auras, trails, and pollination dances.

## OSC Channel Format

The system expects OSC data with channels:
```
p0x, p0y  - Person 0 (X, Y coordinates)
p1x, p1y  - Person 1
p2x, p2y  - Person 2
...
p8x, p8y  - Person 8
```

**Z coordinate:** Ignored (only X and Y are used)

## TouchDesigner Setup

### 1. Create OSC In CHOP

1. In TouchDesigner, create: **CHOP** → **OSC In**
2. Set parameters:
   - **Network Port:** 9000 (or match your mocap system)
   - **Protocol:** UDP
   - **Channels:** Auto (will create channels as OSC data arrives)

### 2. Name the OSC In CHOP

Name it: `mocap_osc_input`

### 3. Connect to Pollination System

Replace the `scale_to_canvas` Math CHOP input with `mocap_osc_input`:

**Current flow (test mode):**
```
mouse_input → scale_to_canvas → pollination_system
```

**Mocap flow (production mode):**
```
mocap_osc_input → pollination_system
```

**Note:** You can keep both connected and switch via the config flag.

### 4. OSC Data Format

Your mocap system should send OSC messages like:
```
/p0x 0.5      # Person 0 X coordinate (0.0 to 1.0)
/p0y 0.3      # Person 0 Y coordinate (0.0 to 1.0)
/p1x 0.7      # Person 1 X coordinate
/p1y 0.8      # Person 1 Y coordinate
...
```

**Important:** Coordinates should be normalized to 0.0-1.0 range representing the physical space.

## Configuration

### Enable Mocap Mode

Edit `config.py`:

```python
# Set to True to use mocap input
USE_MOCAP_INPUT = True
```

### Configure Mocap Settings

```python
MAX_VISITORS = 9  # Total number of tracked people
OSC_PORT = 9000   # Match your mocap system's OSC port

# If mocap sends different coordinate ranges, adjust these:
MOCAP_X_MIN = 0.0
MOCAP_X_MAX = 1.0
MOCAP_Y_MIN = 0.0
MOCAP_Y_MAX = 1.0
```

## Testing Mocap Integration

### Test with OSC Simulator

You can test OSC input before connecting real mocap:

1. Download TouchOSC or similar OSC testing tool
2. Configure to send to: `localhost:9000`
3. Send test messages:
   ```
   /p0x 0.5
   /p0y 0.5
   /p1x 0.3
   /p1y 0.7
   ```

4. Watch TouchDesigner - you should see channels appear in the OSC In CHOP

### Verify in TouchDesigner

1. Open the OSC In CHOP
2. Check **Info CHOP** → you should see channels: `p0x, p0y, p1x, p1y, ...`
3. Values should update when mocap balls move
4. Watch the pollination render - each person should have:
   - Position indicator (yellow ring)
   - Colored aura after touching structures
   - Colored trail when moving
   - Pollination dance effect when switching colors

## Coordinate Mapping

### Physical Space → Canvas Mapping

The system automatically maps mocap coordinates to canvas:

```python
# Mocap space (physical room):
X: 0.0 (left) to 1.0 (right)
Y: 0.0 (top) to 1.0 (bottom)

# Maps to canvas:
X: 0 to 1138/1920 pixels (depending on resolution mode)
Y: 0 to 1280/2160 pixels
```

### Adjusting Mapping

If your mocap system uses different coordinate ranges, edit `config.py`:

```python
# Example: Mocap sends meters (0 to 5m)
MOCAP_X_MIN = 0.0
MOCAP_X_MAX = 5.0
MOCAP_Y_MIN = 0.0
MOCAP_Y_MAX = 5.0
```

The system will automatically normalize these to canvas coordinates.

## Switching Modes

### Test Mode (Development)
```python
USE_MOCAP_INPUT = False
```
- Uses mouse for one visitor
- Shows 3 autonomous agents
- Good for development without mocap

### Production Mode (Live)
```python
USE_MOCAP_INPUT = True
```
- Uses OSC mocap data for all 9 visitors
- No autonomous agents (all tracked via mocap)
- Ready for live installation

## Troubleshooting

### No visitors appearing

1. Check OSC In CHOP is receiving data (values should change)
2. Verify channel names match pattern: `p0x, p0y, p1x, p1y`
3. Check `USE_MOCAP_INPUT = True` in config.py
4. Verify OSC port matches (default 9000)

### Visitors in wrong positions

1. Check coordinate range in config.py
2. Verify mocap sends normalized 0-1 values
3. Test with known position (e.g., center = 0.5, 0.5)

### Missing channels

1. Check mocap system is sending OSC data
2. Verify network connection (firewall, IP address)
3. Use OSC monitor to verify messages arriving

## Network Configuration

### Same Machine
```
OSC Address: 127.0.0.1 (localhost)
Port: 9000
```

### Different Machines
```
OSC Address: [TouchDesigner machine IP]
Port: 9000
Ensure firewall allows UDP on port 9000
```

## Production Checklist

Before going live:

- [ ] OSC In CHOP created and named `mocap_osc_input`
- [ ] OSC port set to match mocap system (default 9000)
- [ ] `USE_MOCAP_INPUT = True` in config.py
- [ ] `USE_PRODUCTION_RESOLUTION = True` for final output
- [ ] Test all 9 visitors can be tracked
- [ ] Verify pollination effects work for all visitors
- [ ] Check trails and auras appear correctly
- [ ] Test network connection stability

## What Stays the Same

When switching to mocap mode:
- ✅ All visual effects (auras, trails, dances)
- ✅ Color collection and pollination logic
- ✅ Structure positions and colors
- ✅ Rendering system
- ✅ Resolution configuration

Only the **input source** changes!
