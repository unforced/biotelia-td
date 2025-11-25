"""
Biotelia Pollination System - TouchDesigner Integration
Main system controller
"""

import sys
import os

# Add biotelia-td to path FIRST before any imports
biotelia_path = '/Users/unforced/Symbols/Codes/biotelia-td'
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

    # Use config defaults if not specified
    if width is None:
        width = config.DEFAULT_WIDTH
    if height is None:
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
    mode = "PRODUCTION" if config.USE_PRODUCTION_RESOLUTION else "TEST"
    print(f"✓ Biotelia Pollination System initialized ({mode} mode)")
    print(f"  - Canvas: {width}x{height}")
    print(f"  - Structures: {len(config.STRUCTURES)}")
    print(f"  - Agents: 3 (bee, butterfly, moth)")

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

    if config.USE_MOCAP_INPUT:
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
