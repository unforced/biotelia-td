#!/usr/bin/env python3
"""
Biotelia Pollination System - Standalone Preview Application

Run this to test the visualization with Pygame.
Use mouse to drag people around, number keys to add/remove people.

Controls:
  - Mouse: Click and drag people
  - 0-8: Set number of people
  - +/-: Adjust intensity
  - SPACE: Pause/unpause
  - S: Save screenshot
  - ESC/Q: Quit
"""

import pygame
import sys
import time
from core import PollinationSystem
from render import PygameRenderer
from input import InputSimulator
import config

def main():
    # Configuration
    width = config.DEFAULT_WIDTH
    height = config.DEFAULT_HEIGHT
    fps = config.TARGET_FPS
    
    # Initialize systems
    print("🌸 Initializing Biotelia Pollination System...")
    
    # Create pollination system
    system = PollinationSystem(
        canvas_width=width,
        canvas_height=height,
        structures_config=config.STRUCTURES
    )
    
    # Add autonomous agents
    system.add_autonomous_agent('bee')
    system.add_autonomous_agent('butterfly')
    system.add_autonomous_agent('moth')
    print(f"✓ Added {len(system.agents)} autonomous pollinators")
    
    # Create renderer
    renderer = PygameRenderer(width, height, tuple(config.BACKGROUND_COLOR))
    renderer.intensity = config.INTENSITY
    
    # Create input simulator
    input_sim = InputSimulator(width, height, num_people=4)
    
    # Main loop
    clock = pygame.time.Clock()
    running = True
    paused = False
    last_time = time.time()
    
    print("✓ System ready!")
    print("\nControls:")
    print("  - Mouse: Click and drag people")
    print("  - 0-8: Set number of people")
    print("  - +/-: Adjust intensity")
    print("  - SPACE: Pause/unpause")
    print("  - S: Save screenshot")
    print("  - ESC/Q: Quit")
    print("\n🚀 Starting visualization...\n")
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    print(f"{'Paused' if paused else 'Resumed'}")
                elif event.key == pygame.K_s:
                    filename = f"biotelia_{int(time.time())}.png"
                    pygame.image.save(renderer.screen, filename)
                    print(f"Screenshot saved: {filename}")
                elif event.key in [pygame.K_PLUS, pygame.K_EQUALS]:
                    renderer.intensity = min(1.0, renderer.intensity + 0.1)
                    print(f"Intensity: {renderer.intensity:.1f}")
                elif event.key == pygame.K_MINUS:
                    renderer.intensity = max(0.0, renderer.intensity - 0.1)
                    print(f"Intensity: {renderer.intensity:.1f}")
                elif pygame.K_0 <= event.key <= pygame.K_8:
                    num = event.key - pygame.K_0
                    while len(input_sim.people) < num:
                        input_sim.add_person()
                    while len(input_sim.people) > num:
                        input_sim.remove_person()
                    print(f"People: {len(input_sim.people)}")
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                input_sim.handle_mouse_down(mouse_x, mouse_y)
                
            elif event.type == pygame.MOUSEBUTTONUP:
                input_sim.handle_mouse_up()
                
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                input_sim.handle_mouse_motion(mouse_x, mouse_y)
                
        if not paused:
            # Calculate dt
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            dt = min(dt, 0.1)  # Cap at 100ms
            
            # Update input simulator
            input_sim.update(dt)
            
            # Get visitor positions
            visitor_positions = input_sim.get_positions()
            
            # Update pollination system
            render_data = system.update(visitor_positions, dt)
            
            # Render
            renderer.render(render_data)
            
        # Maintain frame rate
        clock.tick(fps)
        
    # Cleanup
    renderer.close()
    print("\n👋 Biotelia shutdown complete")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        sys.exit(0)
