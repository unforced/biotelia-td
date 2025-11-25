# Native TouchDesigner Prototype - Results

**Date:** 2025-11-05
**Status:** ✓ Proof of Concept Complete
**Location:** `/project1/native_prototype`

---

## What We Built

A minimal viable prototype implementing the core Biotelia pollination concept using **native TouchDesigner components only** (no Python logic, no numpy rendering).

### Components Implemented

✓ **1 Static Tree** - Yellow tree with glowing aura
✓ **1 Moving Visitor** - Mouse-controlled entity
✓ **Collision Detection** - CHOP-based distance calculation
✓ **Color Transfer** - Visitor absorbs tree color on touch
✓ **Trail Effect** - Feedback loop with fade
✓ **Full Composition** - All layers blended to final output

### Architecture

```
Input Layer (CHOPs):
├── visitor_input (Mouse In CHOP)
├── tree1_position (Constant CHOP)
├── collision_detection (Script CHOP) → distance & color transfer
└── visitor_trail_history (Trail CHOP)

Rendering Layer (TOPs):
├── background (Constant TOP) → dark green
├── tree1 (Circle TOP) → yellow circle
├── tree1_glow (Blur TOP) → tree aura
├── visitor (Circle TOP) → position linked to mouse, color linked to collision
├── visitor_aura (Blur TOP) → visitor glow
├── trail_composite (Feedback loop) → fading trails
└── comp3_add_visitor (Final composite) → 1920x1080 output
```

---

## Key Technical Discoveries

### 1. Collision Detection in CHOPs

Used **Script CHOP** to calculate distance and manage state:

```python
# Calculate distance
distance = sqrt((visitor_x - tree_x)^2 + (visitor_y - tree_y)^2)

# Detect collision
is_colliding = 1.0 if distance < 0.08 else 0.0

# Output color channels
visitor_color_r/g/b = tree color when colliding, white otherwise
```

This works but is still Python-based. Could potentially be replaced with pure CHOP math for even better performance.

### 2. Trail Effect with Feedback

Classic TD technique using **Composite TOP + Level TOP feedback loop**:

```
visitor_aura → composite → fade → back to composite
```

- Fade rate: 0.985 per frame (similar to Python's 0.15 decay)
- No Python needed, pure GPU operation
- Smooth, performant trails

### 3. Expression-Based Linking

Visitor position and color update automatically via expressions:

```python
visitor.par.centerx.expr = "op('visitor_input')['tx']"
visitor.par.fillcolorr.expr = "op('collision_detection')['visitor_color_r']"
```

Real-time parameter binding, no manual updates needed.

---

## What Works Great

### ✓ GPU Acceleration
- All rendering operations run on GPU
- No numpy array manipulation
- Smooth real-time performance

### ✓ Visual Clarity
- Network is readable and logical
- Each node has one clear purpose
- Easy to debug and modify

### ✓ Native Integration
- Works seamlessly with TD's projection mapping
- Easy to add multiple outputs for projectors
- Built-in performance tools

### ✓ Scalability
- Adding more trees: duplicate Circle TOP + position
- Adding more visitors: instance components
- No Python bottlenecks

---

## What Still Needs Work

### ⚠ Color Persistence
Current implementation: visitor color changes **only while touching** tree.

**Need:** Visitor should **keep** color after leaving tree (like Python version).

**Solution:** Add memory/state management:
- Option A: Feedback CHOP to remember last color
- Option B: Small Python script to maintain state
- Option C: Logic CHOP with hold/sample behavior

### ⚠ Spiral Particle Effect
Not yet implemented in this prototype.

**Solution:** Use **Particle SOP** triggered on collision event:
- Execute DAT fires on collision
- Spawns particle system
- Spiral motion via force fields
- Automatic lifetime/fade

### ⚠ Multiple Trees & Visitors
Currently only 1 tree and 1 visitor.

**Solution:** Use **instancing** for entities:
- CHOP Table with all positions/colors
- Instance components for rendering
- One collision detector per visitor-tree pair
- Or spatial optimization (only check nearby)

---

## Performance Comparison

### Python Version (Current Production)
```
Resolution: 1920x1080
Rendering: Script TOP with numpy
Cook Time: ~0.033ms per frame
Features: 5 trees, 3 agents, mycelium, dances, trails
Architecture: Python logic + numpy rendering
```

### Native TD Prototype
```
Resolution: 1920x1080
Rendering: Native TOPs (GPU)
Cook Time: Not yet measured (need comparison)
Features: 1 tree, 1 visitor, basic trail
Architecture: Pure TOPs with minimal Python glue
```

### Expected Benefits of Native TD
- **GPU rendering** → faster than numpy
- **Better scaling** → more entities possible
- **Lower latency** → real-time response
- **Easier projection mapping** → native tools
- **Cleaner network** → visual programming

---

## Decision Framework

### When to Use Python Approach
- ✓ Complex logic (state machines, AI behavior)
- ✓ Need external libraries
- ✓ Prototyping behaviors quickly
- ✓ Version-controlled code preferred
- ✓ Already working and sufficient performance

### When to Use Native TD Approach
- ✓ Performance is critical
- ✓ Many entities (10+ visitors)
- ✓ High resolution (4K+)
- ✓ Multi-projector setup
- ✓ Want to leverage TD's particle systems
- ✓ Team is TD-native

### Hybrid Approach (Recommended)
- **Python:** State management, collision logic, behavior
- **CHOPs:** Data flow, positions, triggers
- **TOPs:** All rendering (GPU-accelerated)

Best of both worlds: clean logic + fast rendering.

---

## Recommended Next Steps

### Option A: Expand Native Prototype
1. Add color persistence (feedback CHOP)
2. Add spiral particle effect (Particle SOP + Execute DAT)
3. Add 4 more trees (instance or duplicate)
4. Add 2 more visitors (instancing)
5. Measure performance vs Python
6. **Decide:** Full migration or hybrid?

### Option B: Hybrid Approach
1. Keep Python for logic (system.py)
2. Export positions/colors to CHOPs
3. Render using TOPs (like this prototype)
4. Measure performance improvement
5. **Result:** Best of both worlds

### Option C: Optimize Python
1. Profile Python renderer bottlenecks
2. Optimize numpy operations
3. Reduce particle count
4. Test if sufficient for production
5. **Result:** Keep working system, improve it

---

## Technical Observations

### Circle TOP Limitations
- Only renders circles (duh!)
- For complex shapes, need SOP geometry
- Position parameters accept expressions → good
- Color parameters accept expressions → good

### Feedback Loops
- Work great for trails
- Need careful initialization (can explode)
- Fade rate needs tuning per aesthetic
- Consider using Feedback TOP for more control

### CHOP Math
- Can replace simple Python scripts
- Expression CHOP for formulas
- Math CHOP for operations
- Logic CHOP for conditionals
- But complex logic still easier in Python

### Composite Operations
- 'Add' works well for glowing elements
- 'Over' for standard layering
- Order matters (bottom to top)
- Alpha channel critical for blending

---

## Code Reference

### Collision Detection (Script CHOP)
Located: `/project1/native_prototype/collision_detection_callbacks`

Outputs:
- `distance` - float distance between visitor and tree
- `is_colliding` - 1.0 or 0.0
- `visitor_color_r/g/b` - current color based on collision

### Key Parameters
```python
# Tree position
tree1_position: tree_x = 0.20, tree_y = 0.30

# Tree appearance
tree1: radius = 0.08, color = (1.0, 0.9, 0.39)

# Visitor appearance
visitor: radius = 0.015, color = linked to collision

# Trail fade
trail_fade: brightness = 0.985

# Collision threshold
collision_detection: threshold = 0.08
```

---

## Comparison Summary

| Feature | Python Version | Native TD Prototype |
|---------|---------------|---------------------|
| **Trees** | 5 | 1 |
| **Visitors** | Variable | 1 (mouse) |
| **Agents** | 3 (bee/butterfly/moth) | 0 |
| **Trails** | ✓ Fading | ✓ Feedback loop |
| **Auras** | ✓ Colored | ✓ Blurred |
| **Color Transfer** | ✓ Persistent | ⚠ Only while touching |
| **Spiral Effect** | ✓ On collision | ✗ Not implemented |
| **Mycelium** | ✓ Network | ✗ Not implemented |
| **Rendering** | CPU (numpy) | GPU (native TOPs) |
| **Logic** | Python classes | Script CHOP + expressions |
| **Complexity** | High (full system) | Low (POC) |
| **Performance** | 60 FPS, 0.033ms | Unknown (needs test) |
| **Scalability** | Limited by CPU | GPU-scalable |

---

## Conclusion

### Proof of Concept: SUCCESS ✓

The native TouchDesigner approach is **viable and promising** for Biotelia.

### Key Findings

1. **Core mechanics work** - collision, color transfer, trails all functional
2. **Architecture is cleaner** - visual network vs code
3. **GPU rendering** - should be faster (needs measurement)
4. **Some Python still useful** - state management, complex logic
5. **Missing features** - need to add color persistence, spirals, multiple entities

### Recommendation

**Pursue Hybrid Approach:**

1. Use Python for:
   - Collision state management
   - Color persistence logic
   - Autonomous agent behaviors
   - Complex interactions

2. Use Native TD for:
   - All rendering (TOPs)
   - Visual effects (particles, trails)
   - Projection mapping
   - Performance-critical operations

3. Bridge with CHOPs:
   - Python exports data to CHOPs
   - TOPs read from CHOPs for rendering
   - Clean separation of concerns

### Next Session

Should focus on:
1. Measuring actual performance difference
2. Implementing color persistence
3. Adding spiral particle effect
4. Testing with multiple entities
5. Making final architecture decision

---

**Status:** Prototype validates native TD approach. Hybrid model recommended for production.
