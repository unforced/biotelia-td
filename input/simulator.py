"""
Input simulator - generates fake visitor positions for testing
"""

import random
import math

class InputSimulator:
    """Simulates mocap input by moving people around the canvas."""
    
    def __init__(self, canvas_width, canvas_height, num_people=4):
        """
        Initialize input simulator.
        
        Args:
            canvas_width, canvas_height: Canvas dimensions
            num_people: Number of simulated people
        """
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.people = []
        self.dragging_person = None
        
        # Create initial people
        for i in range(num_people):
            self.people.append({
                'id': i,
                'x': random.uniform(200, canvas_width - 200),
                'y': random.uniform(200, canvas_height - 200),
                'vx': random.uniform(-20, 20),
                'vy': random.uniform(-20, 20),
            })
            
    def update(self, dt):
        """Update simulated people positions."""
        for person in self.people:
            if person == self.dragging_person:
                continue
                
            # Simple wandering movement
            person['vx'] += random.uniform(-10, 10) * dt
            person['vy'] += random.uniform(-10, 10) * dt
            
            # Limit speed
            speed = math.sqrt(person['vx']**2 + person['vy']**2)
            max_speed = 60
            if speed > max_speed:
                person['vx'] = (person['vx'] / speed) * max_speed
                person['vy'] = (person['vy'] / speed) * max_speed
                
            # Update position
            person['x'] += person['vx'] * dt
            person['y'] += person['vy'] * dt
            
            # Bounce off walls
            margin = 50
            if person['x'] < margin or person['x'] > self.canvas_width - margin:
                person['vx'] *= -0.8
                person['x'] = max(margin, min(self.canvas_width - margin, person['x']))
            if person['y'] < margin or person['y'] > self.canvas_height - margin:
                person['vy'] *= -0.8
                person['y'] = max(margin, min(self.canvas_height - margin, person['y']))
                
            # Damping
            person['vx'] *= 0.95
            person['vy'] *= 0.95
            
    def get_positions(self):
        """Get current positions of all people."""
        return [{'id': p['id'], 'x': p['x'], 'y': p['y']} for p in self.people]
        
    def handle_mouse_down(self, mouse_x, mouse_y):
        """Handle mouse click to drag a person."""
        for person in self.people:
            dx = mouse_x - person['x']
            dy = mouse_y - person['y']
            if math.sqrt(dx*dx + dy*dy) < 20:
                self.dragging_person = person
                return True
        return False
        
    def handle_mouse_up(self):
        """Handle mouse release."""
        self.dragging_person = None
        
    def handle_mouse_motion(self, mouse_x, mouse_y):
        """Handle mouse drag."""
        if self.dragging_person:
            self.dragging_person['x'] = mouse_x
            self.dragging_person['y'] = mouse_y
            self.dragging_person['vx'] = 0
            self.dragging_person['vy'] = 0
            
    def add_person(self):
        """Add a new person."""
        new_id = max([p['id'] for p in self.people]) + 1 if self.people else 0
        self.people.append({
            'id': new_id,
            'x': random.uniform(200, self.canvas_width - 200),
            'y': random.uniform(200, self.canvas_height - 200),
            'vx': random.uniform(-20, 20),
            'vy': random.uniform(-20, 20),
        })
        
    def remove_person(self):
        """Remove a person."""
        if self.people:
            self.people.pop()
