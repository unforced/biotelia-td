"""
MovementTrail - Colored trail following visitors as they move
"""

import numpy as np
import math

class MovementTrail:
    """
    Manages the movement trail behind a visitor.
    Trail uses the visitor's current bioluminescent color and fades slowly.
    """
    
    def __init__(self, person_id, aura, max_points=80, min_distance=8, fade_rate=0.15, point_size=6):
        """
        Initialize movement trail.
        
        Args:
            person_id: Unique identifier for this person
            aura: VisitorAura instance for this person
            max_points: Maximum number of trail points
            min_distance: Minimum distance between points (pixels)
            fade_rate: How fast trail fades (higher = faster)
            point_size: Base size of trail points
        """
        self.person_id = person_id
        self.aura = aura
        self.max_points = max_points
        self.min_distance = min_distance
        self.fade_rate = fade_rate
        self.point_size = point_size
        
        # Trail data
        self.points = []  # List of {x, y, color, life, max_life, time}
        self.last_position = None  # (x, y) of last recorded position
        
    def update(self, person_x, person_y, dt):
        """
        Update trail - add new points, fade existing points.
        
        Args:
            person_x: Person's current X position
            person_y: Person's current Y position
            dt: Delta time in seconds
        """
        # Only record trail if person has a color
        if not self.aura.has_color():
            # Fade out existing trail
            for point in self.points:
                point['life'] -= dt * 0.5
            self.points = [p for p in self.points if p['life'] > 0]
            return
            
        # Check if moved enough to add new point
        if self.last_position is not None:
            dx = person_x - self.last_position[0]
            dy = person_y - self.last_position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > self.min_distance:
                # Add new trail point
                self.points.append({
                    'x': person_x,
                    'y': person_y,
                    'color': self.aura.get_color().copy(),
                    'life': 1.0,
                    'max_life': 1.0,
                    'time': 0.0,  # Age of this point
                })
                
                self.last_position = (person_x, person_y)
                
                # Remove oldest points
                if len(self.points) > self.max_points:
                    self.points.pop(0)
        else:
            # First position
            self.last_position = (person_x, person_y)
            
        # Update existing points (gentle fade)
        for point in self.points:
            point['life'] -= dt * self.fade_rate
            point['time'] += dt
            
        # Remove dead points
        self.points = [p for p in self.points if p['life'] > 0]
        
    def get_render_data(self):
        """
        Get list of trail points for rendering.
        
        Returns:
            List of dictionaries with point data
        """
        render_data = []
        for point in self.points:
            alpha = point['life'] / point['max_life']
            size = self.point_size * (0.5 + alpha * 0.5)
            
            render_data.append({
                'x': point['x'],
                'y': point['y'],
                'color': point['color'],
                'alpha': alpha,
                'size': size,
            })
            
        return render_data
