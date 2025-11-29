"""
Pygame-based renderer for standalone preview
"""

import pygame
import numpy as np
import math

class PygameRenderer:
    """Renders the pollination system using Pygame."""
    
    def __init__(self, width, height, background_color=(10, 15, 8)):
        """
        Initialize Pygame renderer.
        
        Args:
            width, height: Window dimensions
            background_color: RGB background color
        """
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Biotelia Pollination System")
        self.background_color = background_color
        self.intensity = 0.7
        
    def clear(self):
        """Clear the screen."""
        self.screen.fill(self.background_color)
        
    def render(self, render_data):
        """
        Render all visual elements.
        
        Args:
            render_data: Dictionary from PollinationSystem.get_render_data()
        """
        self.clear()
        
        # Render layers in order (bottom to top)
        self._render_mycelium(render_data.get('mycelium', []))
        self._render_visitor_trails(render_data.get('visitor_trails', []))
        self._render_dances(render_data.get('dances', []))
        self._render_structures(render_data.get('structures', []))
        self._render_visitor_auras(render_data.get('visitor_auras', []))
        self._render_agents(render_data.get('agents', []))
        self._render_visitors(render_data.get('visitors', []))
        
        pygame.display.flip()
        
    def _render_mycelium(self, mycelium_data):
        """Render mycelial network lines and particles."""
        for connection in mycelium_data:
            line = connection['line']
            alpha = int(line['flow'] * self.intensity * 255 * 0.3)
            color = (140, 185, 102)
            
            # Draw connection line
            self._draw_line_alpha(
                (line['x1'], line['y1']),
                (line['x2'], line['y2']),
                color,
                alpha,
                1
            )
            
            # Draw flow particles
            for p in connection['particles']:
                p_alpha = int(p['alpha'] * self.intensity * 255 * 0.5)
                self._draw_circle_alpha(
                    (int(p['x']), int(p['y'])),
                    4,
                    color,
                    p_alpha
                )
                
    def _render_visitor_trails(self, trails_data):
        """Render movement trails."""
        for trail_points in trails_data:
            for i, point in enumerate(trail_points):
                alpha = int(point['alpha'] * self.intensity * 255 * 0.6)
                size = int(point['size'])
                
                # Glow
                self._draw_circle_glow(
                    (int(point['x']), int(point['y'])),
                    size * 2,
                    tuple(point['color']),
                    int(alpha * 0.4)
                )
                
                # Core
                self._draw_circle_alpha(
                    (int(point['x']), int(point['y'])),
                    size,
                    tuple(point['color']),
                    alpha
                )
                
    def _render_dances(self, dances_data):
        """Render pollination swirl effects."""
        for dance in dances_data:
            # Render rings
            for ring in dance['rings']:
                alpha = int(ring['alpha'] * self.intensity * 255 * 0.5)
                pygame.draw.circle(
                    self.screen,
                    tuple(ring['color']),
                    (int(ring['x']), int(ring['y'])),
                    int(ring['radius']),
                    3
                )
                
            # Render swirl particles
            for p in dance['particles']:
                alpha = int(p['alpha'] * self.intensity * 255)
                size = int(p['size'])
                
                # Glow
                self._draw_circle_glow(
                    (int(p['x']), int(p['y'])),
                    size * 2,
                    tuple(p['color']),
                    int(alpha * 0.5)
                )
                
                # Core
                self._draw_circle_alpha(
                    (int(p['x']), int(p['y'])),
                    size,
                    tuple(p['color']),
                    alpha
                )
                
    def _render_structures(self, structures_data):
        """Render tree/mushroom structures."""
        for structure in structures_data:
            x, y = int(structure['x']), int(structure['y'])
            radius = int(structure['radius'] * structure['pulse'])
            color = tuple(structure['color'])
            energy = structure['energy']
            
            # Outer glow
            glow_alpha = int(energy * self.intensity * 255 * 0.3)
            self._draw_circle_glow(
                (x, y),
                int(radius * 1.5),
                color,
                glow_alpha
            )
            
            # Ring
            pygame.draw.circle(self.screen, color, (x, y), radius, 3)
            
            # Core
            pygame.draw.circle(self.screen, color, (x, y), 12)
            
    def _render_visitor_auras(self, auras_data):
        """Render visitor bioluminescent auras."""
        for aura in auras_data:
            if aura is None:
                continue
                
            x, y = int(aura['x']), int(aura['y'])
            color = tuple(aura['color'])
            intensity = aura['intensity']
            radius = int(aura['glow_radius'] * aura['pulse'])
            
            # Outer glow
            outer_alpha = int(intensity * self.intensity * 255 * 0.4)
            self._draw_circle_glow(
                (x, y),
                radius * 2,
                color,
                outer_alpha
            )
            
            # Inner glow
            inner_alpha = int(intensity * self.intensity * 255 * 0.6)
            self._draw_circle_glow(
                (x, y),
                int(radius * 1.5),
                color,
                inner_alpha
            )
            
    def _render_agents(self, agents_data):
        """Render autonomous pollinators."""
        for agent in agents_data:
            x, y = int(agent['x']), int(agent['y'])
            
            # Render trail
            for trail_point in agent['trail']:
                alpha = int(trail_point['alpha'] * self.intensity * 255 * 0.4)
                size = int(trail_point['size'])
                self._draw_circle_alpha(
                    (int(trail_point['x']), int(trail_point['y'])),
                    size,
                    tuple(trail_point['color']),
                    alpha
                )
                
            # Render glow if carrying color
            if agent['glow'] is not None:
                glow = agent['glow']
                glow_radius = int(glow['radius'] * glow['pulse'])
                glow_alpha = int(glow['intensity'] * self.intensity * 255 * 0.4)
                
                self._draw_circle_glow(
                    (x, y),
                    glow_radius * 2,
                    tuple(glow['color']),
                    glow_alpha
                )
                
            # Agent body
            pygame.draw.circle(
                self.screen,
                tuple(agent['base_color']),
                (x, y),
                agent['size']
            )
            
    def _render_visitors(self, visitors_data):
        """Render person position indicators."""
        for visitor in visitors_data:
            x, y = int(visitor['x']), int(visitor['y'])
            
            # Indicator circle
            pygame.draw.circle(
                self.screen,
                (255, 230, 100),
                (x, y),
                12,
                2
            )
            
    def _draw_circle_alpha(self, pos, radius, color, alpha):
        """Draw a circle with alpha transparency."""
        if alpha <= 0 or radius <= 0:
            return
        alpha = min(255, max(0, alpha))
        surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, (*color, alpha), (radius, radius), radius)
        self.screen.blit(surface, (pos[0] - radius, pos[1] - radius))
        
    def _draw_circle_glow(self, pos, radius, color, alpha):
        """Draw a glowing circle (simplified blur)."""
        if alpha <= 0 or radius <= 0:
            return
        alpha = min(255, max(0, alpha))
        
        # Draw multiple circles with decreasing alpha for glow effect
        for i in range(3):
            r = radius - i * 2
            if r > 0:
                a = alpha // (i + 1)
                self._draw_circle_alpha(pos, r, color, a)
                
    def _draw_line_alpha(self, start, end, color, alpha, width):
        """Draw a line with alpha transparency."""
        if alpha <= 0:
            return
        alpha = min(255, max(0, alpha))
        
        # Calculate line surface size
        x1, y1 = start
        x2, y2 = end
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx * dx + dy * dy)
        
        if length < 1:
            return
            
        # Create surface and draw line
        surf_width = int(abs(dx) + width + 10)
        surf_height = int(abs(dy) + width + 10)
        surface = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
        
        offset_x = min(x1, x2) - width - 5
        offset_y = min(y1, y2) - width - 5
        
        pygame.draw.line(
            surface,
            (*color, alpha),
            (int(x1 - offset_x), int(y1 - offset_y)),
            (int(x2 - offset_x), int(y2 - offset_y)),
            width
        )
        
        self.screen.blit(surface, (offset_x, offset_y))
        
    def close(self):
        """Clean up Pygame."""
        pygame.quit()
