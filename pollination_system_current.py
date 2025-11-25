"""
Biotelia Pollination System - TouchDesigner Integration
Main system controller
"""

import sys
import os

# Add biotelia-td to path FIRST before any imports
# Use dynamic path resolution based on .toe file location
def get_project_path():
    """Get the biotelia-td project path dynamically."""
    # Try to get from TouchDesigner project location
    try:
        # Get the .toe file's parent directory
        toe_path = project.folder
        if toe_path and os.path.exists(toe_path):
            return toe_path
    except:
        pass

    # Fallback: try to find based on this file's location
    try:
        # This DAT is in /project1/pollination_system
        # The biotelia-td folder should be the .toe file's location
        return os.path.dirname(os.path.abspath(__file__))
    except:
        pass

    # Final fallback to hardcoded path (for development)
    return '/Users/unforced/Symbols/Codes/biotelia-td'

biotelia_path = get_project_path()
if biotelia_path not in sys.path:
    sys.path.insert(0, biotelia_path)

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
            # Use TD parameter
            use_production = (settings.par.Resmode.eval() == 1)  # 1 = production
            width = config.PRODUCTION_WIDTH if use_production else config.TEST_WIDTH
        else:
            # Fallback to config
            width = config.DEFAULT_WIDTH

    if height is None:
        if settings and hasattr(settings.par, 'Resmode'):
            use_production = (settings.par.Resmode.eval() == 1)
            height = config.PRODUCTION_HEIGHT if use_production else config.TEST_HEIGHT
        else:
            height = config.DEFAULT_HEIGHT

    # Create system with configured resolution
    system = PollinationSystem(
        canvas_width=width,
        canvas_height=height,
        structures_config=config.STRUCTURES
    )

    # Add autonomous agents
    system.add_autonomous_agent('bee')
    system.add_autonomous_agent('butterfly')
    system.add_autonomous_agent('moth')

    initialized = True

    # Determine mode from actual resolution
    mode = "PRODUCTION" if width == config.PRODUCTION_WIDTH else "TEST"

    print(f"✓ Biotelia Pollination System initialized ({mode} mode)")
    print(f"  - Canvas: {width}x{height}")
    print(f"  - Structures: {len(config.STRUCTURES)}")
    print(f"  - Agents: 3 (bee, butterfly, moth)")

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
        # Use TD parameter: 0 = mouse, 1 = mocap
        use_mocap = (settings.par.Inputmode.eval() == 1)
    else:
        # Fallback to config
        use_mocap = config.USE_MOCAP_INPUT

    if use_mocap:
        # PRODUCTION MODE: Parse mocap data (p0x, p0y, p1x, p1y, ...)
        for person_id in range(config.MAX_VISITORS):
            try:
                # Get channels for this person
                x_channel_name = f'p{person_id}x'
                y_channel_name = f'p{person_id}y'

                x_chan = chop_data.chan(x_channel_name)
                y_chan = chop_data.chan(y_channel_name)

                if x_chan and y_chan:
                    # Get raw mocap values
                    x_raw = x_chan.eval() if hasattr(x_chan, 'eval') else x_chan[0]
                    y_raw = y_chan.eval() if hasattr(y_chan, 'eval') else y_chan[0]

                    # Map mocap coordinates to canvas
                    # Assuming mocap sends normalized 0-1 values
                    x = x_raw * config.DEFAULT_WIDTH
                    y = y_raw * config.DEFAULT_HEIGHT

                    # Add visitor
                    visitors.append({
                        'id': person_id,
                        'x': x,
                        'y': y,
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
