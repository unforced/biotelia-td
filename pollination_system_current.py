"""
Biotelia Pollination System - TouchDesigner Integration
Main system controller
"""

import sys
import os

# Add biotelia-td to path FIRST before any imports
# Use dynamic path resolution based on .toe file location
try:
    # Get the .toe file's parent directory
    biotelia_path = project.folder
    if not biotelia_path or not os.path.exists(biotelia_path):
        raise RuntimeError(
            f"ERROR: Cannot determine project path. project.folder is: {biotelia_path}\n"
            "Make sure the .toe file is saved to disk and all biotelia-td files are in the same folder."
        )
except Exception as e:
    raise RuntimeError(
        f"ERROR: Failed to get project path: {e}\n"
        "The .toe file must be saved in the biotelia-td folder with core/, config.py, etc."
    )

if biotelia_path not in sys.path:
    sys.path.insert(0, biotelia_path)

print(f"✓ Project path: {biotelia_path}")

# NOW import the modules
from core.system import PollinationSystem
import config
import numpy as np

# Global system instance
system = None
initialized = False

def initialize(width=None, height=None):
    """Initialize the pollination system (call once)."""
    global system, initialized

    if initialized:
        return

    # Get settings from TouchDesigner UI if available
    settings = op('/project1/settings_control')

    # Use config defaults if not specified
    if width is None:
        if settings and hasattr(settings.par, 'Resmode'):
            # Use TD parameter (string: "test" or "production")
            use_production = (settings.par.Resmode.eval() == "production")
            width = config.PRODUCTION_WIDTH if use_production else config.TEST_WIDTH
        else:
            # Fallback to config
            width = config.DEFAULT_WIDTH

    if height is None:
        if settings and hasattr(settings.par, 'Resmode'):
            use_production = (settings.par.Resmode.eval() == "production")
            height = config.PRODUCTION_HEIGHT if use_production else config.TEST_HEIGHT
        else:
            height = config.DEFAULT_HEIGHT

    # Create system with configured resolution
    system = PollinationSystem(
        canvas_width=width,
        canvas_height=height,
        structures_config=config.STRUCTURES
    )

    # Add autonomous agents only in test mode
    # In production/mocap mode, only mocap-tracked visitors are shown
    if settings and hasattr(settings.par, 'Inputmode'):
        use_mocap = (settings.par.Inputmode.eval() == "mocap")
    else:
        use_mocap = config.USE_MOCAP_INPUT

    num_agents = 0
    if not use_mocap:
        # Test mode: add autonomous agents
        system.add_autonomous_agent('bee')
        system.add_autonomous_agent('butterfly')
        system.add_autonomous_agent('moth')
        num_agents = 3

    initialized = True

    # Determine mode from actual resolution
    mode = "PRODUCTION" if width == config.PRODUCTION_WIDTH else "TEST"

    print(f"✓ Biotelia Pollination System initialized ({mode} mode)")
    print(f"  - Canvas: {width}x{height}")
    print(f"  - Structures: {len(config.STRUCTURES)}")
    if num_agents > 0:
        print(f"  - Agents: {num_agents} (bee, butterfly, moth)")
    else:
        print(f"  - Agents: 0 (mocap mode - visitors only)")

    # Show settings source
    if settings and hasattr(settings.par, 'Resmode'):
        print(f"  - Settings: TouchDesigner UI (/project1/settings_control)")
    else:
        print(f"  - Settings: config.py (fallback)")

def update_frame(chop_data, dt=1.0/60.0):
    """
    Update pollination system each frame.

    Args:
        chop_data: CHOP with position data
                   Mouse mode: channels tx, ty
                   Mocap mode: channels p0x, p0y, p1x, p1y, ... p8x, p8y
        dt: Delta time in seconds

    Returns:
        Render data dictionary
    """
    global system

    if not initialized:
        initialize()

    # Parse visitor positions from CHOP
    visitors = []

    if not chop_data or not hasattr(chop_data, 'chan'):
        # No input data, return with empty visitors
        render_data = system.update(visitors, dt)
        return render_data

    # Get input mode from TouchDesigner UI if available
    settings = op('/project1/settings_control')
    use_mocap = False

    if settings and hasattr(settings.par, 'Inputmode'):
        # Use TD parameter (string: "mouse" or "mocap")
        use_mocap = (settings.par.Inputmode.eval() == "mocap")
    else:
        # Fallback to config
        use_mocap = config.USE_MOCAP_INPUT

    if use_mocap:
        # PRODUCTION MODE: Parse mocap data (p1x, p1y, p2x, p2y, ...)
        # Channel names start at 1, not 0
        for person_id in range(1, config.MAX_VISITORS + 1):
            try:
                # Get channels for this person
                x_channel_name = f'p{person_id}x'
                y_channel_name = f'p{person_id}y'

                x_chan = chop_data.chan(x_channel_name)
                y_chan = chop_data.chan(y_channel_name)

                if x_chan and y_chan:
                    # Get mocap values (already mapped to pixel coordinates in TD)
                    x_val = x_chan.eval() if hasattr(x_chan, 'eval') else x_chan[0]
                    y_val = y_chan.eval() if hasattr(y_chan, 'eval') else y_chan[0]

                    # Coordinates are already mapped to pixels in TouchDesigner
                    visitors.append({
                        'id': person_id - 1,
                        'x': x_val,
                        'y': y_val,
                    })
            except Exception as e:
                # Channel not found or error - skip this person
                pass
    else:
        # TEST MODE: Use mouse input for single visitor
        try:
            tx_chan = chop_data.chan('tx')
            ty_chan = chop_data.chan('ty')

            if tx_chan and ty_chan:
                x = tx_chan.eval() if hasattr(tx_chan, 'eval') else tx_chan[0]
                y = ty_chan.eval() if hasattr(ty_chan, 'eval') else ty_chan[0]

                visitors.append({
                    'id': 0,
                    'x': x,
                    'y': y,
                })
        except Exception as e:
            # No valid position data yet
            pass

    # Update system
    render_data = system.update(visitors, dt)

    return render_data

def get_render_info():
    """Get information about what needs to be rendered."""
    if not initialized:
        return None

    return {
        'canvas_width': config.DEFAULT_WIDTH,
        'canvas_height': config.DEFAULT_HEIGHT,
        'num_structures': len(config.STRUCTURES),
        'structures': config.STRUCTURES,
    }

# Auto-initialize on load with configured resolution
initialize()
