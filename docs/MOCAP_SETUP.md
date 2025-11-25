# Mocap Setup Guide

**Status:** ✓ Ready for mocap integration
**Input:** OSC (X, Y coordinates)
**Output:** `/project1/gpu_renderer/OUT` (1920x1080)

---

## Quick Summary

✓ **3 trees** positioned near exhibit edges
✓ **Larger auras** (40px radius, 100px tree radius)
✓ **Trail system** working - pollinators leave colored trails
✓ **OSC input** ready on port 7000
✓ **Mouse testing** mode available

---

## Current Configuration

### Trees (3 structures near edges)
- **Tree 1:** Top-left (15%, 20%) - Yellow
- **Tree 2:** Top-right (85%, 25%) - Pink
- **Tree 3:** Bottom-center (50%, 80%) - Purple

Each tree:
- Radius: 100px (larger collision area)
- Aura glow: 40px (more visible)
- Alpha: 0.6 (semi-transparent)

### Trail Behavior
- **Max points:** 80
- **Fade rate:** 0.15 (gradual fade)
- **Point size:** 6px
- **Color:** Inherits from last touched tree
- **Persistence:** Color stays until touching another tree

---

## How to Use

### Testing Mode (Mouse)
**Current setting** - For development

1. Move mouse over TouchDesigner window
2. Mouse position = one pollinator
3. Move over trees to pick up colors
4. Watch trail follow behind with that color

### Production Mode (OSC Mocap)
**Switch when ready** - For exhibit

1. Change `input_mode` parameter:
   - Select `/project1/input_mode` node
   - Set `use_osc` parameter to **1**

2. Send OSC messages to **port 7000**:
   - Format: `/pollinator/0/x` value
   - Format: `/pollinator/0/y` value
   - (Z coordinate ignored for now)

3. Multiple pollinators:
   - `/pollinator/1/x`, `/pollinator/1/y`
   - `/pollinator/2/x`, `/pollinator/2/y`
   - etc.

---

## OSC Message Format

### Expected Format
```
/pollinator/0/x  <float 0-1920>
/pollinator/0/y  <float 0-1080>
/pollinator/1/x  <float 0-1920>
/pollinator/1/y  <float 0-1080>
```

### Coordinate System
- **X:** 0 = left edge, 1920 = right edge
- **Y:** 0 = top edge, 1080 = bottom edge
- **Origin:** Top-left corner

### OSC Settings
- **Port:** 7000
- **Protocol:** UDP
- **Address:** localhost (or specific IP)

To change port:
1. Select `/project1/mocap_osc_input`
2. Modify `port` parameter

---

## Network Flow

```
INPUT MODE (testing vs production)
    ↓
┌─────────────────┐
│  Mouse (0)      │ ← Testing
│       OR        │
│  OSC (1)        │ ← Production (mocap)
└────────┬────────┘
         │
    input_switch
         │
         ↓
  pollination_system (Python logic)
         │
         ↓
    Table DATs (data)
         │
         ↓
   gpu_renderer (optimized)
         │
         ↓
       OUTPUT (1920x1080)
```

---

## How Trail Colors Work

### Behavior
1. **Initial state:** Pollinator has no color (neutral)
2. **Touch tree:** Pollinator absorbs tree's color into aura
3. **Move away:** Trail appears behind pollinator in that color
4. **Trail fades:** Gradually over time (80 points max)
5. **Touch different tree:**
   - Aura changes to new color
   - Trail switches to new color
   - Old trail continues fading with old color

### Visual Result
You'll see:
- Pollinator dot (yellow indicator)
- Colored aura around pollinator (from last tree)
- Colored trail following behind
- Cross-pollination when visiting different trees

---

## Current Status Check

Run this in TextPort to verify:

```python
# Check trees
op('/project1/structures_data').numRows  # Should be 4 (header + 3 trees)

# Check input mode
op('/project1/input_mode')['use_osc'][0]  # 0=mouse, 1=OSC

# Check output
op('/project1/gpu_renderer/OUT')  # Should show scene

# Check if data is flowing
op('/project1/trails_data').numRows  # Should increase when moving
```

---

## Switching Between Mouse and OSC

### Method 1: Via Parameter
1. Select `/project1/input_mode` node
2. Change `use_osc` value:
   - **0** = Mouse (testing)
   - **1** = OSC (mocap)

### Method 2: Via Python
```python
op('/project1/input_mode').par.const0value = 1  # Switch to OSC
op('/project1/input_mode').par.const0value = 0  # Switch to Mouse
```

---

## Troubleshooting

### "Not seeing any output in gpu_renderer"
- Check `/project1/gpu_renderer/OUT` viewer
- Verify frame_timer is running
- Check tables have data (structures_data should have 4 rows)

### "Trail not showing color"
- Move mouse/pollinator over a tree first
- Tree auras are now larger (100px radius)
- Check trails_data table - should have entries when moving

### "OSC not working"
1. Verify OSC messages reaching TouchDesigner:
   - Check `/project1/mocap_osc_input` - should show channels
2. Verify input_mode is set to 1 (OSC)
3. Check OSC port matches sender (default: 7000)

### "Colors not persisting"
- This is correct! Colors fade over time (0.995 decay rate)
- Touch tree again to refresh color
- To make colors last longer, edit config.py:
  - Increase `AURA_DECAY_RATE` (closer to 1.0 = longer)

---

## File Locations

### Configuration
- **Tree positions:** `/Users/unforced/Symbols/Codes/biotelia-td/config.py`
  - Edit `STRUCTURES` array
  - Edit `AURA_GLOW_RADIUS` for aura size

### Input Settings
- **OSC port:** `/project1/mocap_osc_input` - port parameter
- **Input mode:** `/project1/input_mode` - use_osc parameter

### Output
- **Primary output:** `/project1/gpu_renderer/OUT`
- **Resolution:** 1920x1080
- **Format:** RGBA 32-bit float

---

## Next Steps for Production

### Before Exhibit Opens
1. **Test OSC input:**
   - Send test messages to port 7000
   - Verify pollinators appear and move

2. **Set input to OSC:**
   - Change `input_mode` use_osc to 1

3. **Position projectors:**
   - Use `/project1/gpu_renderer/OUT` as source
   - Map to exhibit space

4. **Adjust if needed:**
   - Tree positions in config.py
   - Aura sizes
   - Trail lengths

### During Exhibit
- Input mode: OSC (1)
- OSC messages: Continuous stream of X,Y coordinates
- System updates: 60 FPS
- Trails: Automatically fade and update

---

## Summary

**✓ System Ready**
- 3 trees near exhibit edges
- Larger auras (more visible)
- Trail color persistence working
- OSC input configured (port 7000)
- Mouse testing available

**To Start Exhibit:**
1. Switch input_mode to OSC (set use_osc = 1)
2. Send mocap coordinates to port 7000
3. Project `/project1/gpu_renderer/OUT`

**Trail System:**
- Pollinators pick up tree colors on touch
- Leave colored trails as they move
- Trails fade gradually
- Colors change when visiting different trees
