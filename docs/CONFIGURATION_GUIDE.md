# Configuration Guide - Native TD Prototype

**Location:** `/project1/native_prototype`
**Status:** ✓ Fully Configurable
**Date:** 2025-11-05

---

## Quick Start

The native TD prototype now has **two simple configuration points**:

1. **`tree_config`** - Table DAT for static tree positions and colors
2. **`pollinator_input`** - Component for dynamic position input (mouse or mocap)

---

## 📋 Tree Configuration

**Location:** `/project1/native_prototype/tree_config`

### Table Format

```
id    x      y      radius    color_hex
0     0.20   0.30   0.08      FFE664
1     0.75   0.25   0.08      FF8CB4
2     0.50   0.50   0.08      B478FF
3     0.25   0.75   0.07      64FFB4
4     0.80   0.70   0.07      FFB464
```

### Columns

- **id** - Tree identifier (0-4)
- **x** - X position (0.0 to 1.0, normalized)
- **y** - Y position (0.0 to 1.0, normalized)
- **radius** - Tree radius (0.0 to 1.0, normalized)
- **color_hex** - 6-digit hex color code (no # symbol)

### Example Colors

| Name | Hex Code | RGB |
|------|----------|-----|
| Yellow | FFE664 | 255, 230, 100 |
| Pink | FF8CB4 | 255, 140, 180 |
| Purple | B478FF | 180, 120, 255 |
| Cyan | 64FFB4 | 100, 255, 180 |
| Orange | FFB464 | 255, 180, 100 |

### How to Change

1. **In TouchDesigner:**
   - Open `/project1/native_prototype/tree_config`
   - Click any cell to edit
   - Changes apply immediately

2. **Position:** (0,0) = bottom-left, (1,1) = top-right
3. **Radius:** Typical range 0.05-0.10 for visible trees
4. **Color:** Use any hex color (e.g., FF0000 = red)

### Adding More Trees

Currently only Tree 0 is rendered (first tree in table). To render more trees:
- Duplicate the tree1/tree1_glow network
- Update scripts to read from different rows
- OR wait for instancing implementation (next step)

---

## 🎮 Pollinator Input

**Location:** `/project1/native_prototype/pollinator_input`

### Current Setup

```
pollinator_input/
├── mouse_source (Mouse In CHOP) ← ACTIVE
├── mocap_source (Null CHOP) ← Ready for future
├── input_selector (Select CHOP) ← Switches between sources
└── OUT (Null CHOP) ← Output channels: tx, ty
```

### Output Channels

- **tx** - X position (0.0 to 1.0)
- **ty** - Y position (0.0 to 1.0)

### Current Source: Mouse

Mouse position normalized to canvas. Works immediately for testing.

### Switching to Mocap

**Step 1:** Connect your mocap system

```
Your mocap CHOP → pollinator_input/mocap_source
```

**Step 2:** Switch the selector

```python
# In TouchDesigner
op('pollinator_input/input_selector').par.chops = 'mocap_source'
```

**Done!** The system now reads from mocap.

### Mocap Channel Format

Expected channels from your mocap system:

**Option A: Single Pollinator**
```
tx - X position (0-1)
ty - Y position (0-1)
```

**Option B: Multiple Pollinators**
```
person0_x, person0_y
person1_x, person1_y
person2_x, person2_y
...
```

If using Option B, you'll need to update the rendering to handle multiple entities (instancing).

---

## 🔄 How It Works

### Data Flow

```
tree_config (Table DAT)
    ↓
    ├→ tree1 (Circle TOP) - position & color
    ├→ tree1_position (Constant CHOP) - for collision
    └→ collision_detection (Script CHOP) - color on touch

pollinator_input/OUT (CHOP)
    ↓
    ├→ visitor (Circle TOP) - position
    ├→ visitor_trail_history (Trail CHOP) - trail effect
    └→ collision_detection (Script CHOP) - distance calc
```

### Collision Detection

Located: `/project1/native_prototype/collision_detection`

Reads:
- `pollinator_input/OUT` for visitor position
- `tree1_position` for tree position
- `tree_config` for tree color and radius

Outputs:
- `distance` - Distance between visitor and tree
- `is_colliding` - 1.0 when touching, 0.0 otherwise
- `visitor_color_r/g/b` - Color visitor should be

### Rendering

All visual elements read from these sources automatically:
- Tree color/position from `tree_config`
- Visitor color from `collision_detection`
- Visitor position from `pollinator_input/OUT`

**Change the config → visuals update instantly!**

---

## 🎨 Common Adjustments

### Change Tree Color

1. Open `tree_config`
2. Find the tree row (1-5)
3. Edit `color_hex` column
4. Example: Change to red = `FF0000`

### Move Tree

1. Open `tree_config`
2. Edit `x` or `y` columns
3. Values: 0.0 (left/bottom) to 1.0 (right/top)

### Adjust Tree Size

1. Open `tree_config`
2. Edit `radius` column
3. Larger = bigger tree (try 0.10)
4. Smaller = smaller tree (try 0.05)

### Test with Keyboard/Other Input

Replace `mouse_source` with any CHOP that outputs `tx, ty` channels:
- Keyboard CHOP (arrow keys)
- OSC In CHOP (external control)
- MIDI CHOP (MIDI controller)
- Constant CHOP (manual control)

---

## 📊 Configuration Examples

### Example 1: Three Trees in Triangle

```
id    x      y      radius    color_hex
0     0.50   0.20   0.10      FF0000
1     0.30   0.70   0.10      00FF00
2     0.70   0.70   0.10      0000FF
```

### Example 2: Five Trees in Circle

```
id    x      y      radius    color_hex
0     0.50   0.20   0.08      FFE664
1     0.80   0.38   0.08      FF8CB4
2     0.70   0.75   0.08      B478FF
3     0.30   0.75   0.08      64FFB4
4     0.20   0.38   0.08      FFB464
```

### Example 3: Linear Path

```
id    x      y      radius    color_hex
0     0.20   0.50   0.08      FF0000
1     0.35   0.50   0.08      FF7F00
2     0.50   0.50   0.08      FFFF00
3     0.65   0.50   0.08      00FF00
4     0.80   0.50   0.08      0000FF
```

---

## 🚀 Next Steps

### Currently Implemented
- ✓ Single tree from config table
- ✓ Single visitor/pollinator
- ✓ Mouse input with easy mocap swap
- ✓ Collision detection
- ✓ Color transfer on touch
- ✓ Trail effects

### To Add (Future)
- [ ] Render all 5 trees from table (instancing)
- [ ] Multiple pollinators (instancing)
- [ ] Color persistence after leaving tree
- [ ] Spiral particle effects on collision
- [ ] Autonomous agents (bees, butterflies)

---

## 💡 Pro Tips

### Tip 1: Live Editing

The system updates **in real-time**. No need to restart or re-cook anything. Just edit the table!

### Tip 2: Save Presets

To save tree configurations:
1. Right-click `tree_config`
2. Save to file
3. Load different configs as needed

### Tip 3: Mocap Scaling

If your mocap gives different ranges (e.g., -1 to 1 or pixel coords), add a Math CHOP before `mocap_source` to normalize to 0-1.

### Tip 4: Multiple Visitors

To add more visitors:
1. Extend `tree_config` format to include pollinator configs
2. OR create separate `pollinator_config` table
3. Use instancing to render multiple entities

---

## 🔧 Troubleshooting

### Trees Not Showing

- Check `tree_config` values are valid (0-1 range)
- View `tree1` and `tree1_glow` nodes
- Ensure `comp3_add_visitor` is connected

### Visitor Not Moving

- Check `pollinator_input/OUT` has `tx, ty` channels
- Verify `mouse_source` is active
- Check `visitor` expression links

### Colors Not Changing

- Verify `collision_detection` is cooking
- Check distance < radius when touching tree
- View `collision_detection` CHOP output channels

### Mocap Not Working

- Ensure mocap CHOP connected to `mocap_source`
- Switch `input_selector.par.chops` to `'mocap_source'`
- Check channel names match (tx, ty)
- Add Math CHOP to scale if needed

---

## 📞 Quick Reference

| What | Where |
|------|-------|
| Tree positions/colors | `/project1/native_prototype/tree_config` |
| Pollinator input | `/project1/native_prototype/pollinator_input` |
| Switch to mocap | `pollinator_input/input_selector.par.chops` |
| Final output | `/project1/native_prototype/comp3_add_visitor` |
| Collision logic | `/project1/native_prototype/collision_detection` |

---

**All set! Your prototype is now fully configurable and ready for mocap integration.**
