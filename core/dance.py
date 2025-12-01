"""
PollinationDance - Swirl effect when visitor color meets new tree color
"""

import numpy as np
import math
import random

class PollinationDance:
    """
    Creates a swirling visual effect when a visitor carrying one color
    touches a structure with a different color.
    """
    
    def __init__(self, x, y, visitor_color, structure_color, duration=2.5, structure_radius=650):
        """
        Initialize pollination dance effect.

        Args:
            x, y: Position of the structure (center of swirl)
            visitor_color: RGB color visitor is carrying
            structure_color: RGB color of the structure
            duration: How long the swirl lasts (seconds)
            structure_radius: Radius of the structure (for edge positioning)
        """
        self.x = x
        self.y = y
        self.visitor_color = np.array(visitor_color, dtype=np.uint8)
        self.structure_color = np.array(structure_color, dtype=np.uint8)
        self.duration = duration
        self.structure_radius = structure_radius
        self.life = 1.0  # 1.0 to 0.0

        # Create swirl particles
        self.particles = self._create_swirl_particles()

        # Create expanding rings
        self.rings = self._create_rings()
        
    def _create_swirl_particles(self):
        """Create particles that swirl at the edge of the structure."""
        particles = []
        particle_count = 60  # More particles for bigger effect

        # Start particles at the edge of the structure circle
        edge_radius = self.structure_radius * 0.85  # Slightly inside edge

        for i in range(particle_count):
            angle = (i / particle_count) * 2 * math.pi
            spiral = i / particle_count  # 0 to 1

            # Alternate between visitor and structure colors
            color = self.visitor_color if i % 2 == 0 else self.structure_color

            # Particles start at edge and spiral outward with variation
            radius_variation = random.uniform(-50, 100)

            particles.append({
                'angle': angle,
                'spiral': spiral,
                'radius': edge_radius + radius_variation + spiral * 80,
                'angular_speed': random.uniform(1.0, 2.0),
                'color': color,
                'life': 1.0,
                'size': random.uniform(12, 24),  # Larger particles
            })

        return particles
    
    def _create_rings(self):
        """Create expanding rings at the edge of the structure."""
        edge_radius = self.structure_radius * 0.85
        return [
            {
                'radius': edge_radius,
                'max_radius': edge_radius + 200,
                'color': self.visitor_color,
                'speed': random.uniform(60, 100),
            },
            {
                'radius': edge_radius - 20,
                'max_radius': edge_radius + 180,
                'color': self.structure_color,
                'speed': random.uniform(60, 100),
            },
        ]
    
    def update(self, dt):
        """
        Update swirl animation.
        
        Args:
            dt: Delta time in seconds
        """
        self.life -= dt / self.duration
        
        # Update swirl particles
        for p in self.particles:
            p['angle'] += p['angular_speed'] * dt * 2  # Swirl around
            p['radius'] += dt * 20  # Expand outward
            p['life'] -= dt / self.duration
            
        # Update rings
        for ring in self.rings:
            ring['radius'] += dt * ring['speed']
            
    def is_dead(self):
        """Check if animation is complete."""
        return self.life <= 0
    
    def get_render_data(self):
        """
        Get data for rendering the swirl effect.
        
        Returns:
            Dictionary with particles and rings data
        """
        alpha = self.life
        
        # Calculate particle positions
        particles_data = []
        for p in self.particles:
            if p['life'] > 0:
                x = self.x + math.cos(p['angle']) * p['radius']
                y = self.y + math.sin(p['angle']) * p['radius']
                
                particles_data.append({
                    'x': x,
                    'y': y,
                    'color': p['color'],
                    'alpha': p['life'] * alpha,
                    'size': p['size'],
                })
                
        # Ring data
        rings_data = []
        for ring in self.rings:
            if ring['radius'] < ring['max_radius']:
                ring_alpha = alpha * (1 - ring['radius'] / ring['max_radius'])
                rings_data.append({
                    'x': self.x,
                    'y': self.y,
                    'radius': ring['radius'],
                    'color': ring['color'],
                    'alpha': ring_alpha,
                })
                
        return {
            'center_x': self.x,
            'center_y': self.y,
            'particles': particles_data,
            'rings': rings_data,
            'visitor_color': self.visitor_color,
            'structure_color': self.structure_color,
            'alpha': alpha,
        }
