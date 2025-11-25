"""
AutonomousAgent - Bees, butterflies, and moths that pollinate independently
"""

import numpy as np
import math
import random
import time

class AutonomousAgent:
    """
    Represents a bee, butterfly, or moth that moves autonomously,
    collects colors from structures, and leaves trails.
    """
    
    def __init__(self, agent_id, agent_type, structures, start_x=None, start_y=None, canvas_size=(1920, 1080)):
        """
        Initialize autonomous pollinator.
        
        Args:
            agent_id: Unique identifier
            agent_type: 'bee', 'butterfly', or 'moth'
            structures: List of Structure objects
            start_x, start_y: Starting position (random if None)
            canvas_size: (width, height) for boundary checking
        """
        self.id = agent_id
        self.type = agent_type
        self.structures = structures
        self.canvas_width, self.canvas_height = canvas_size
        
        # Position and movement
        self.x = start_x if start_x is not None else random.uniform(100, canvas_size[0] - 100)
        self.y = start_y if start_y is not None else random.uniform(100, canvas_size[1] - 100)
        self.target_structure = None
        self.state = 'flying'  # 'flying' or 'collecting'
        self.state_timer = 0.0
        
        # Bioluminescence (same as visitors)
        self.current_color = None
        self.glow_intensity = 0.0
        self.collected_time = 0.0

        # Pollination tracking
        self.last_pollination = None  # Stores {x, y, old_color, new_color} when pollination happens
        
        # Trail (same as human visitors)
        self.trail = []  # List of {x, y, color, life}
        self.max_trail_points = 80  # Match human visitors
        self.last_trail_position = None  # Track distance moved
        self.trail_min_distance = 8  # Minimum pixels before adding point
        
        # Type-specific characteristics
        self._set_characteristics()
        
        # Pick initial target
        self._pick_new_target()
        
    def _set_characteristics(self):
        """Set movement characteristics based on pollinator type."""
        characteristics = {
            'bee': {'speed': 60, 'size': 35, 'wiggle': 0.8, 'color': np.array([255, 220, 60], dtype=np.uint8)},
            'butterfly': {'speed': 40, 'size': 40, 'wiggle': 1.5, 'color': np.array([255, 160, 200], dtype=np.uint8)},
            'moth': {'speed': 50, 'size': 35, 'wiggle': 1.0, 'color': np.array([180, 200, 220], dtype=np.uint8)},
        }
        
        char = characteristics.get(self.type, characteristics['bee'])
        self.speed = char['speed']
        self.size = char['size']
        self.wiggle = char['wiggle']
        self.base_color = char['color']
        
    def _pick_new_target(self):
        """Pick a random structure to fly toward."""
        if not self.structures:
            return
        self.target_structure = random.choice(self.structures)
        self.state = 'flying'
        self.state_timer = random.uniform(3, 8)
        
    def collect_color(self, color):
        """Collect color from structure (same as visitors)."""
        self.current_color = np.array(color, dtype=np.uint8).copy()
        self.glow_intensity = 1.0
        self.collected_time = time.time()
        
    def update(self, dt, current_time, speed_multiplier=0.6):
        """
        Update agent position, state, and bioluminescence.
        
        Args:
            dt: Delta time in seconds
            current_time: Current timestamp
            speed_multiplier: Global speed control
        """
        self.state_timer -= dt
        
        if self.target_structure is None:
            self._pick_new_target()
            return
            
        # Calculate direction to target
        dx = self.target_structure.x - self.x
        dy = self.target_structure.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if self.state == 'flying':
            # Fly toward target with organic wiggle
            wiggle_x = math.sin(current_time * 0.003) * self.wiggle * 20
            wiggle_y = math.cos(current_time * 0.004) * self.wiggle * 20
            
            if distance > 0:
                self.x += (dx / distance) * self.speed * dt * speed_multiplier + wiggle_x * dt
                self.y += (dy / distance) * self.speed * dt * speed_multiplier + wiggle_y * dt
            
            # Arrived at structure?
            if distance < 30:
                self.state = 'collecting'
                self.state_timer = random.uniform(1, 2)
                
        elif self.state == 'collecting':
            # Circle around structure
            circle_angle = current_time * 0.002
            circle_radius = 25
            self.x = self.target_structure.x + math.cos(circle_angle) * circle_radius
            self.y = self.target_structure.y + math.sin(circle_angle) * circle_radius

            # Finished collecting?
            if self.state_timer <= 0:
                # Check if this is a different color (pollination event!)
                new_color = self.target_structure.color
                if self.current_color is not None:
                    # Check if different color
                    is_different = not np.array_equal(self.current_color, new_color)
                    if is_different:
                        # Store pollination event for system to create dance
                        self.last_pollination = {
                            'x': self.target_structure.x,
                            'y': self.target_structure.y,
                            'old_color': self.current_color.copy(),
                            'new_color': np.array(new_color, dtype=np.uint8)
                        }

                self.collect_color(new_color)
                self._pick_new_target()
                
        # Keep in bounds
        self.x = max(50, min(self.canvas_width - 50, self.x))
        self.y = max(50, min(self.canvas_height - 50, self.y))
        
        # Update bioluminescence decay
        if self.glow_intensity > 0:
            decay_factor = 0.998 ** (dt * 60)
            self.glow_intensity *= decay_factor
            if self.glow_intensity < 0.05:
                self.glow_intensity = 0.0
                self.current_color = None
                
        # Update trail (same logic as human visitors)
        if self.current_color is not None and self.glow_intensity > 0:
            # Add trail point based on distance moved (not randomly)
            if self.last_trail_position is not None:
                dx = self.x - self.last_trail_position[0]
                dy = self.y - self.last_trail_position[1]
                distance = math.sqrt(dx * dx + dy * dy)

                if distance > self.trail_min_distance:
                    self.trail.append({
                        'x': self.x,
                        'y': self.y,
                        'color': self.current_color.copy(),
                        'life': 1.0,
                    })
                    self.last_trail_position = (self.x, self.y)

                    if len(self.trail) > self.max_trail_points:
                        self.trail.pop(0)
            else:
                # First position
                self.last_trail_position = (self.x, self.y)
        else:
            # Fade out existing trail when no color
            for point in self.trail:
                point['life'] -= dt * 0.5
            self.trail = [p for p in self.trail if p['life'] > 0]
            return

        # Fade trail (same rate as human visitors: 0.15)
        for point in self.trail:
            point['life'] -= dt * 0.15
        self.trail = [p for p in self.trail if p['life'] > 0]
        
    def get_render_data(self, current_time):
        """Get data for rendering this agent."""
        trail_data = []
        for point in self.trail:
            trail_data.append({
                'x': point['x'],
                'y': point['y'],
                'color': point['color'],
                'alpha': point['life'],
                'size': 3 + point['life'] * 2,
            })
            
        # Glow data
        glow_data = None
        if self.current_color is not None and self.glow_intensity > 0:
            pulse = 1 + math.sin((current_time - self.collected_time) * 2) * 0.1
            glow_data = {
                'color': self.current_color,
                'intensity': self.glow_intensity,
                'radius': self.size * 2,
                'pulse': pulse,
            }
            
        return {
            'x': self.x,
            'y': self.y,
            'size': self.size,
            'base_color': self.base_color,
            'trail': trail_data,
            'glow': glow_data,
        }
