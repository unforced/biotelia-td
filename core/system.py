"""
PollinationSystem - Main orchestrator for the pollination visualization
"""

import time
import numpy as np
from .structure import Structure
from .aura import VisitorAura
from .trail import MovementTrail
from .dance import PollinationDance
from .agent import AutonomousAgent
from .mycelium import MycelialNetwork

class PollinationSystem:
    """
    Main system that orchestrates all pollination visualization components.
    Receives position data and produces render data.
    """
    
    def __init__(self, canvas_width=1920, canvas_height=1080, structures_config=None):
        """
        Initialize the pollination system.
        
        Args:
            canvas_width: Canvas width in pixels
            canvas_height: Canvas height in pixels
            structures_config: List of structure dicts with {id, x, y, radius, color}
        """
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.time = 0.0
        self.start_time = time.time()
        
        # Create structures
        self.structures = []
        if structures_config:
            for s in structures_config:
                # Scale normalized positions to canvas size
                x = s['x'] * canvas_width if s['x'] <= 1.0 else s['x']
                y = s['y'] * canvas_height if s['y'] <= 1.0 else s['y']
                self.structures.append(Structure(s['id'], x, y, s['radius'], s['color']))
                
        # Create mycelial network
        self.mycelial_network = MycelialNetwork(self.structures)
        
        # Visitor tracking
        self.visitor_auras = {}  # person_id -> VisitorAura
        self.visitor_trails = {}  # person_id -> MovementTrail
        
        # Active pollination dances
        self.dances = []
        
        # Autonomous agents
        self.agents = []
        
        # Settings
        self.intensity = 0.7
        self.speed = 0.6
        
    def add_autonomous_agent(self, agent_type):
        """Add a bee, butterfly, or moth."""
        agent_id = len(self.agents)
        agent = AutonomousAgent(
            agent_id, 
            agent_type, 
            self.structures,
            canvas_size=(self.canvas_width, self.canvas_height)
        )
        self.agents.append(agent)
        return agent
        
    def _colors_match(self, color1, color2):
        """Check if two RGB colors match."""
        return np.array_equal(color1, color2)
        
    def update(self, visitor_positions, dt=None):
        """
        Update the entire system.
        
        Args:
            visitor_positions: List of dicts with {id, x, y}
            dt: Delta time in seconds (auto-calculated if None)
            
        Returns:
            Complete render data for all visual elements
        """
        # Calculate dt if not provided
        if dt is None:
            current_time = time.time()
            dt = current_time - (self.start_time + self.time)
            dt = min(dt, 0.1)  # Cap at 100ms
            
        self.time += dt
        current_timestamp = time.time()
        
        # Update structures
        for structure in self.structures:
            structure.update(dt, self.time)
            
        # Update mycelial network
        self.mycelial_network.update(dt, self.time)
        
        # Update visitors
        active_visitor_ids = set()
        for visitor in visitor_positions:
            person_id = visitor['id']
            px, py = visitor['x'], visitor['y']
            active_visitor_ids.add(person_id)
            
            # Create aura and trail if new
            if person_id not in self.visitor_auras:
                self.visitor_auras[person_id] = VisitorAura(person_id)
            if person_id not in self.visitor_trails:
                aura = self.visitor_auras[person_id]
                self.visitor_trails[person_id] = MovementTrail(person_id, aura)
                
            aura = self.visitor_auras[person_id]
            trail = self.visitor_trails[person_id]
            
            # Check collisions with structures
            for structure in self.structures:
                if structure.contains_point(px, py):
                    # Check if different color (pollination!)
                    current_color = aura.get_color()
                    is_different = current_color is not None and not self._colors_match(current_color, structure.color)
                    
                    if is_different and aura.has_color():
                        # Create pollination dance
                        dance = PollinationDance(
                            structure.x,
                            structure.y,
                            current_color,
                            structure.color
                        )
                        self.dances.append(dance)
                        
                    # Collect new color
                    aura.collect_color(structure.color)
                    
            # Update aura and trail
            aura.update(dt)
            trail.update(px, py, dt)
            
        # Remove auras/trails for visitors who left
        for person_id in list(self.visitor_auras.keys()):
            if person_id not in active_visitor_ids:
                del self.visitor_auras[person_id]
                del self.visitor_trails[person_id]
                
        # Update dances
        for dance in self.dances:
            dance.update(dt)
        self.dances = [d for d in self.dances if not d.is_dead()]
        
        # Update autonomous agents
        for agent in self.agents:
            agent.update(dt, current_timestamp, self.speed)
            
        # Return complete render data
        return self.get_render_data(visitor_positions, current_timestamp)
        
    def get_render_data(self, visitor_positions, current_time):
        """
        Get all rendering data.
        
        Returns:
            Dictionary with all visual elements
        """
        return {
            'mycelium': self.mycelial_network.get_render_data(),
            'structures': [s.get_render_data(self.time) for s in self.structures],
            'visitor_auras': [
                self.visitor_auras[v['id']].get_render_data(v['x'], v['y'], current_time)
                for v in visitor_positions if v['id'] in self.visitor_auras
            ],
            'visitor_trails': [
                self.visitor_trails[v['id']].get_render_data()
                for v in visitor_positions if v['id'] in self.visitor_trails
            ],
            'dances': [d.get_render_data() for d in self.dances],
            'agents': [a.get_render_data(current_time) for a in self.agents],
            'visitors': visitor_positions,  # Pass through for person indicators
        }
