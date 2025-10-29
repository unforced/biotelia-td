"""
VisitorAura - Bioluminescent glow around visitors carrying tree colors
"""

import numpy as np
import time
import math

class VisitorAura:
    """
    Manages the single-color bioluminescent aura around a visitor.
    Aura appears when touching a structure and decays very slowly.
    """
    
    def __init__(self, person_id, glow_radius=18, decay_rate=0.998, min_intensity=0.05):
        """
        Initialize visitor aura.
        
        Args:
            person_id: Unique identifier for this person
            glow_radius: Radius of glow around person (pixels)
            decay_rate: Decay multiplier per frame (0.998 = very slow)
            min_intensity: Intensity threshold for color removal
        """
        self.person_id = person_id
        self.glow_radius = glow_radius
        self.decay_rate = decay_rate
        self.min_intensity = min_intensity
        
        # Current state
        self.current_color = None  # RGB array or None
        self.intensity = 0.0  # 0 to 1
        self.collected_time = 0.0  # Timestamp when color was collected
        
    def collect_color(self, color):
        """
        Collect a new color from a structure.
        Replaces any existing color (visitor carries ONE color at a time).
        
        Args:
            color: numpy array [R, G, B] (0-255)
        """
        self.current_color = np.array(color, dtype=np.uint8).copy()
        self.intensity = 1.0
        self.collected_time = time.time()
        
    def update(self, dt):
        """
        Update aura intensity (very slow decay).
        
        Args:
            dt: Delta time in seconds
        """
        if self.intensity > 0:
            # Very slow decay - 10x longer than original
            # Loses about 20% per 100 seconds
            decay_factor = self.decay_rate ** (dt * 60)
            self.intensity *= decay_factor
            
            # Remove color when extremely faint
            if self.intensity < self.min_intensity:
                self.intensity = 0.0
                self.current_color = None
                
    def has_color(self):
        """Check if visitor currently has a color."""
        return self.current_color is not None and self.intensity > 0
    
    def get_color(self):
        """Get current color (or None)."""
        return self.current_color
    
    def get_intensity(self):
        """Get current intensity (0-1)."""
        return self.intensity
    
    def get_render_data(self, person_x, person_y, current_time):
        """
        Get data needed for rendering this aura.
        
        Args:
            person_x: Person's X position
            person_y: Person's Y position
            current_time: Current timestamp for pulse calculation
            
        Returns:
            Dictionary with rendering info, or None if no aura
        """
        if not self.has_color():
            return None
            
        # Calculate pulse effect
        pulse_phase = (current_time - self.collected_time) * 2.0
        pulse = 1.0 + math.sin(pulse_phase) * 0.1
        
        return {
            'x': person_x,
            'y': person_y,
            'color': self.current_color,
            'intensity': self.intensity,
            'glow_radius': self.glow_radius,
            'pulse': pulse,
        }
