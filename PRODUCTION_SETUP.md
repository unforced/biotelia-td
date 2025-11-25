# Production Setup Guide

## Resolution Configuration

The system is now configured to work with different resolutions for testing vs production deployment.

### Current Setup (Testing)

**Resolution:** 1138 x 1280 (8:9 portrait aspect ratio)
- Within non-commercial TouchDesigner's 1280x1280 limit
- Maintains exact aspect ratio of final production output

### Production Deployment

**Final Resolution:** 1920 x 2160 (8:9 portrait aspect ratio)

## How to Switch to Production Resolution

When moving to the final machine with a commercial TouchDesigner license:

1. Open `config.py`
2. Change line 44:
   ```python
   USE_PRODUCTION_RESOLUTION = False
   ```
   to:
   ```python
   USE_PRODUCTION_RESOLUTION = True
   ```

3. Reload the TouchDesigner project - the system will automatically use 1920x2160

That's it! Everything else stays the same.

## What Changes Automatically

When `USE_PRODUCTION_RESOLUTION = True`:
- ✅ Canvas size: 1920 x 2160
- ✅ All structure positions (use normalized 0-1 coordinates)
- ✅ Agent boundaries
- ✅ Rendering resolution
- ✅ No code changes needed

## Technical Details

The aspect ratio is maintained across both resolutions:
- **Test:** 1138 / 1280 = 0.8890625
- **Production:** 1920 / 2160 = 0.8888...
- Difference: < 0.02%

All positions use normalized coordinates (0.0 to 1.0), so structures and agents scale perfectly.

## Verification

After switching to production mode, check the console output:
```
✓ Biotelia Pollination System initialized (PRODUCTION mode)
  - Canvas: 1920x2160
  - Structures: 3
  - Agents: 3 (bee, butterfly, moth)
```

You should see "PRODUCTION mode" instead of "TEST mode".

## Mocap Integration

For the final installation with mocap tracking, you'll also need to enable mocap input.

### Enable Mocap Input

In `config.py`, change line 51:
```python
USE_MOCAP_INPUT = False
```
to:
```python
USE_MOCAP_INPUT = True
```

This switches from mouse input to OSC mocap input for all 9 visitors (3 robot pollinators + 6 humans).

**See MOCAP_SETUP.md for complete mocap integration guide.**

## Complete Production Checklist

Before going live on the final machine:

**Resolution & Input:**
- [ ] Set `USE_PRODUCTION_RESOLUTION = True` (line 44 in config.py)
- [ ] Set `USE_MOCAP_INPUT = True` (line 51 in config.py)

**TouchDesigner Setup:**
- [ ] Create OSC In CHOP named `mocap_osc_input`
- [ ] Set OSC port to 9000 (or match your mocap system)
- [ ] Connect `mocap_osc_input` to `pollination_system` DAT

**Mocap System:**
- [ ] Configure mocap to send OSC to TouchDesigner machine
- [ ] Verify OSC channels: p0x, p0y, p1x, p1y ... p8x, p8y
- [ ] Test all 9 visitors can be tracked
- [ ] Verify coordinates are normalized (0.0 to 1.0)

**Final Testing:**
- [ ] Check console shows "PRODUCTION mode"
- [ ] Verify output resolution is 1920x2160
- [ ] Test all visitors create auras and trails
- [ ] Confirm pollination dances appear
- [ ] Check network stability

Detailed mocap setup instructions are in **MOCAP_SETUP.md**.
