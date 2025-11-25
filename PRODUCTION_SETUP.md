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
