"""
MycelialNetwork - Background connections between structures
"""

import numpy as np
import math
import random

class MycelialNetwork:
    """
    Represents the always-present mycelial connections between structures.
    Shows that the ecosystem is already alive and connecting.
    """
    
    def __init__(self, structures):
        """
        Initialize mycelial network.
        
        Args:
            structures: List of Structure objects
        """
        self.structures = structures
        self.connections = self._create_connections()
        
    def _create_connections(self):
        """Create connections between nearby structures."""
        connections = []
        max_distance = 2000
        
        for i, struct_a in enumerate(self.structures):
            # Find nearby structures
            nearby = []
            for j, struct_b in enumerate(self.structures):
                if i >= j:
                    continue
                dx = struct_b.x - struct_a.x
                dy = struct_b.y - struct_a.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < max_distance:
                    nearby.append((j, distance, struct_b))
                    
            # Sort by distance
            nearby.sort(key=lambda x: x[1])
            
            # Connect to 2-3 nearest (but only if we have nearby structures)
            if len(nearby) > 0:
                num_connections = min(random.randint(2, 3), len(nearby))
                for k in range(num_connections):
                    if k < len(nearby):
                        _, _, struct_b = nearby[k]
                        connections.append({
                            'struct_a': struct_a,
                            'struct_b': struct_b,
                            'flow': 0.2,
                            'particles': [],
                        })
                    
        return connections
    
    def update(self, dt, time):
        """Update network flow and particles."""
        for conn in self.connections:
            # Gentle flow variation
            conn['flow'] = 0.2 + math.sin(time * 0.3) * 0.1
            
            # Spawn flow particles occasionally
            if random.random() < dt * 0.5:
                conn['particles'].append({
                    'progress': random.choice([0.0, 1.0]),
                    'direction': random.choice([-1, 1]),
                    'life': 3.0,
                })
                
            # Update particles
            for p in conn['particles']:
                p['progress'] += p['direction'] * dt * 0.2
                p['life'] -= dt
                
            # Remove dead particles
            conn['particles'] = [p for p in conn['particles'] if p['life'] > 0 and 0 <= p['progress'] <= 1]
            
    def get_render_data(self):
        """Get data for rendering the network."""
        render_data = []
        
        for conn in self.connections:
            # Line data
            line_data = {
                'x1': conn['struct_a'].x,
                'y1': conn['struct_a'].y,
                'x2': conn['struct_b'].x,
                'y2': conn['struct_b'].y,
                'flow': conn['flow'],
            }
            
            # Particle data
            particles_data = []
            for p in conn['particles']:
                px = conn['struct_a'].x + (conn['struct_b'].x - conn['struct_a'].x) * p['progress']
                py = conn['struct_a'].y + (conn['struct_b'].y - conn['struct_a'].y) * p['progress']
                particles_data.append({
                    'x': px,
                    'y': py,
                    'alpha': p['life'] / 3.0,
                })
                
            render_data.append({
                'line': line_data,
                'particles': particles_data,
            })
            
        return render_data
