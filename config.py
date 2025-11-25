"""
Biotelia Pollination System - Configuration
Colors, structure positions, and system settings
"""

import numpy as np

# Structure colors
STRUCTURE_COLORS = {
    'structure1': np.array([255, 230, 100], dtype=np.uint8),
    'structure2': np.array([255, 140, 180], dtype=np.uint8),
    'structure3': np.array([180, 120, 255], dtype=np.uint8),
    'structure4': np.array([100, 255, 180], dtype=np.uint8),
    'structure5': np.array([255, 180, 100], dtype=np.uint8),
}

# Pollinator colors
POLLINATOR_COLORS = {
    'bee': np.array([255, 220, 60], dtype=np.uint8),
    'butterfly': np.array([255, 160, 200], dtype=np.uint8),
    'moth': np.array([180, 200, 220], dtype=np.uint8),
}

BACKGROUND_COLOR = np.array([10, 15, 8], dtype=np.uint8)
PERSON_INDICATOR_COLOR = np.array([255, 230, 100], dtype=np.uint8)

# Structure positions (normalized 0-1) - 3 trees near exhibit edges
STRUCTURES = [
    {'id': 0, 'x': 0.15, 'y': 0.20, 'radius': 100, 'color': STRUCTURE_COLORS['structure1']},  # Top-left
    {'id': 1, 'x': 0.85, 'y': 0.25, 'radius': 100, 'color': STRUCTURE_COLORS['structure2']},  # Top-right
    {'id': 2, 'x': 0.50, 'y': 0.80, 'radius': 100, 'color': STRUCTURE_COLORS['structure3']},  # Bottom-center
]

# Resolution Settings
# PRODUCTION resolution (requires commercial TouchDesigner license)
PRODUCTION_WIDTH = 1920
PRODUCTION_HEIGHT = 2160  # Portrait 8:9 aspect ratio

# TEST resolution (within non-commercial 1280x1280 limit, same aspect ratio)
TEST_WIDTH = 1138  # Maintains 8:9 aspect ratio
TEST_HEIGHT = 1280

# Current mode: Set to True when deploying to production machine
USE_PRODUCTION_RESOLUTION = False

# Active resolution (automatically selected)
DEFAULT_WIDTH = PRODUCTION_WIDTH if USE_PRODUCTION_RESOLUTION else TEST_WIDTH
DEFAULT_HEIGHT = PRODUCTION_HEIGHT if USE_PRODUCTION_RESOLUTION else TEST_HEIGHT

# Settings
TARGET_FPS = 60
INTENSITY = 0.7
SPEED = 2.0  # Increased for better visibility

# Aura settings
AURA_GLOW_RADIUS = 40  # Larger aura radius for better visibility
AURA_DECAY_RATE = 0.995  # Slightly faster decay (was 0.998)
AURA_MIN_INTENSITY = 0.05

# Trail settings
TRAIL_MAX_POINTS = 80
TRAIL_MIN_DISTANCE = 8
TRAIL_FADE_RATE = 0.15
TRAIL_POINT_SIZE = 6
