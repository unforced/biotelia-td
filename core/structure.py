"""
Structure - Trees and mushrooms that visitors pollinate
"""

import numpy as np
import math

class Structure:
    """Represents a tree or mushroom structure in the ecosystem."""
    
    def __init__(self, struct_id, x, y, radius, color):
        """
        Initialize a structure.
        
        Args:
            struct_id: Unique identifier
            x, y: Position (pixels)
            radius: Collision radius
            color: RGB numpy array
        """
        self.id = struct_id
        self.x = x
        self.y = y
        self.radius = radius
        self.color = np.array(color, dtype=np.uint8)
        self.energy = 0.3  # Breathing energy level
        
    def update(self, dt, time):
        """Update structure (gentle breathing animation)."""
        self.energy = 0.3 + math.sin(time * 0.5) * 0.1
        
    def contains_point(self, px, py):
        """Check if a point is within this structure's radius."""
        dx = px - self.x
        dy = py - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < self.radius
    
    def get_render_data(self, time):
        """Get rendering data for this structure."""
        pulse = 1 + math.sin(time * 2) * 0.1
        return {
            'x': self.x,
            'y': self.y,
            'radius': self.radius,
            'color': self.color,
            'energy': self.energy,
            'pulse': pulse,
        }
