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

# Structure positions (normalized 0-1)
STRUCTURES = [
    {'id': 0, 'x': 0.20, 'y': 0.30, 'radius': 80, 'color': STRUCTURE_COLORS['structure1']},
    {'id': 1, 'x': 0.75, 'y': 0.25, 'radius': 80, 'color': STRUCTURE_COLORS['structure2']},
    {'id': 2, 'x': 0.50, 'y': 0.50, 'radius': 80, 'color': STRUCTURE_COLORS['structure3']},
    {'id': 3, 'x': 0.25, 'y': 0.75, 'radius': 70, 'color': STRUCTURE_COLORS['structure4']},
    {'id': 4, 'x': 0.80, 'y': 0.70, 'radius': 70, 'color': STRUCTURE_COLORS['structure5']},
]

# Settings
DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080
TARGET_FPS = 60
INTENSITY = 0.7
SPEED = 0.6

# Aura settings
AURA_GLOW_RADIUS = 18
AURA_DECAY_RATE = 0.998
AURA_MIN_INTENSITY = 0.05

# Trail settings
TRAIL_MAX_POINTS = 80
TRAIL_MIN_DISTANCE = 8
TRAIL_FADE_RATE = 0.15
TRAIL_POINT_SIZE = 6
