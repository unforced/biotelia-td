# Improved rendering with better trail visibility
import numpy as np

def onCook(scriptOp):
    """Render pollination system with enhanced trail visibility."""

    # Get canvas dimensions from TouchDesigner UI settings or config
    import sys
    import os

    # Add project path dynamically - fail if not found
    try:
        biotelia_path = project.folder
        if not biotelia_path or not os.path.exists(biotelia_path):
            raise RuntimeError(f"Cannot determine project path. project.folder is: {biotelia_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to get project path: {e}")

    if biotelia_path not in sys.path:
        sys.path.insert(0, biotelia_path)

    import config

    # Try to get settings from TouchDesigner UI
    settings = op('/project1/settings_control')

    if settings and hasattr(settings.par, 'Resmode'):
        # Use TouchDesigner parameter (string: "test" or "production")
        use_production = (settings.par.Resmode.eval() == "production")
        width = config.PRODUCTION_WIDTH if use_production else config.TEST_WIDTH
        height = config.PRODUCTION_HEIGHT if use_production else config.TEST_HEIGHT
    else:
        # Fallback to config defaults
        width = config.DEFAULT_WIDTH
        height = config.DEFAULT_HEIGHT

    pollination_dat = op('/project1/pollination_system')
    input_chop = op('/project1/input_switch')

    if not pollination_dat:
        scriptOp.copyNumpyArray(np.zeros((height, width, 4), dtype=np.float32))
        return

    try:
        render_data = pollination_dat.module.update_frame(input_chop, 1.0/60.0)
    except Exception as e:
        scriptOp.copyNumpyArray(np.zeros((height, width, 4), dtype=np.float32))
        return

    # Create canvas with configured dimensions
    canvas = np.zeros((height, width, 4), dtype=np.float32)

    # Background (dark forest floor)
    canvas[:, :, 0] = 10 / 255.0
    canvas[:, :, 1] = 15 / 255.0
    canvas[:, :, 2] = 8 / 255.0
    canvas[:, :, 3] = 1.0

    # Get time for trail flow animation
    import time
    import random
    import math
    flow_time = time.time()

    # Seed random for consistent particle positions per frame
    # (particles stay in same relative positions but float)

    # === RENDER LAYERS ===

    # 1. Structures (trees) - floating particles within circle radius
    for struct_idx, structure in enumerate(render_data.get('structures', [])):
        x, y = int(structure['x']), int(structure['y'])
        radius = int(structure['radius'])
        color = structure['color']

        # Generate floating particles within the circle
        num_particles = 120  # Number of particles per tree

        for i in range(num_particles):
            # Use deterministic seed for each particle (consistent positions)
            seed = struct_idx * 1000 + i

            # Base position within circle (polar coordinates)
            # Use golden ratio for even distribution
            golden_angle = math.pi * (3 - math.sqrt(5))
            theta_base = i * golden_angle
            # Distribute radius with sqrt for even area coverage
            r_base = math.sqrt((i + 0.5) / num_particles) * radius * 0.95

            # Add floating animation
            float_speed = 0.3 + (seed % 100) / 200.0  # Varying speeds
            float_amp = 20 + (seed % 50)  # Varying amplitudes

            # Orbital drift
            theta = theta_base + math.sin(flow_time * float_speed + seed) * 0.3
            r = r_base + math.sin(flow_time * float_speed * 0.7 + seed * 0.1) * float_amp

            # Convert to cartesian
            px = int(x + math.cos(theta) * r)
            py = int(y + math.sin(theta) * r)

            # Particle size varies (bigger)
            particle_size = 12 + (seed % 10)

            # Alpha varies by distance from center and time (brighter)
            dist_factor = 1.0 - (r / radius) * 0.2
            pulse = 0.7 + math.sin(flow_time * 2 + seed * 0.5) * 0.3
            alpha = 0.8 * dist_factor * pulse

            # Draw particle with glow (larger glow radius)
            draw_circle_additive(canvas, px, py, particle_size * 2.5, color, alpha * 0.5)
            draw_circle_additive(canvas, px, py, particle_size * 1.5, color, alpha * 0.7)
            draw_circle_additive(canvas, px, py, particle_size, color, alpha)

    # 2. Agent trails (with watery flow!)
    for agent_idx, agent in enumerate(render_data.get('agents', [])):
        for point_idx, point in enumerate(agent.get('trail', [])):
            # Add wavy displacement to create flowing water effect
            wave_freq = 0.02  # Frequency of waves
            wave_amp = 12  # Amplitude of waves

            # Multiple wave layers for more organic flow
            wave1 = math.sin((point['x'] * wave_freq) + (flow_time * 2) + (agent_idx * 0.5)) * wave_amp
            wave2 = math.cos((point['y'] * wave_freq * 0.7) + (flow_time * 1.5) + (point_idx * 0.1)) * wave_amp * 0.6
            wave3 = math.sin((point_idx * 0.3) + (flow_time * 3)) * wave_amp * 0.4

            # Apply watery displacement
            x = int(point['x'] + wave1 + wave3)
            y = int(point['y'] + wave2 - wave3)

            color = point['color']
            alpha = point['alpha']
            size = int(point['size'])

            # Watery trails with larger glow
            # Outer glow (very soft)
            draw_circle_additive(canvas, x, y, size * 4, color, alpha * 0.3)
            # Middle glow
            draw_circle_additive(canvas, x, y, size * 2, color, alpha * 0.5)
            # Core
            draw_circle_additive(canvas, x, y, size, color, alpha * 0.7)

    # 3. Visitor trails (with watery flow!)
    for trail_idx, trail_points in enumerate(render_data.get('visitor_trails', [])):
        for point_idx, point in enumerate(trail_points):
            # Same watery flow effect
            wave_freq = 0.02
            wave_amp = 12

            wave1 = math.sin((point['x'] * wave_freq) + (flow_time * 2) + (trail_idx * 0.5)) * wave_amp
            wave2 = math.cos((point['y'] * wave_freq * 0.7) + (flow_time * 1.5) + (point_idx * 0.1)) * wave_amp * 0.6
            wave3 = math.sin((point_idx * 0.3) + (flow_time * 3)) * wave_amp * 0.4

            x = int(point['x'] + wave1 + wave3)
            y = int(point['y'] + wave2 - wave3)

            color = point['color']
            alpha = point['alpha']
            size = int(point['size'])

            # Watery trails with larger glow
            draw_circle_additive(canvas, x, y, size * 4, color, alpha * 0.3)
            draw_circle_additive(canvas, x, y, size * 2, color, alpha * 0.5)
            draw_circle_additive(canvas, x, y, size, color, alpha * 0.7)

    # 4. Visitor auras (color from touching trees)
    for aura in render_data.get('visitor_auras', []):
        if aura is not None:
            x, y = int(aura['x']), int(aura['y'])
            color = aura['color']
            intensity = aura['intensity']
            radius = int(aura['glow_radius'] * aura['pulse'] * 4)  # Sized to match white aura

            # Large glow
            draw_circle_additive(canvas, x, y, radius * 3, color, intensity * 0.3)
            # Medium glow
            draw_circle_additive(canvas, x, y, radius * 2, color, intensity * 0.5)
            # Inner glow
            draw_circle_additive(canvas, x, y, radius, color, intensity * 0.7)

    # 5. Agents (bee/butterfly/moth) with glows
    for agent in render_data.get('agents', []):
        x, y = int(agent['x']), int(agent['y'])

        # Agent glow (if carrying color)
        if agent.get('glow') is not None:
            glow = agent['glow']
            glow_radius = int(glow['radius'] * glow['pulse'])
            glow_color = glow['color']
            glow_intensity = glow['intensity']

            # Large glow
            draw_circle_additive(canvas, x, y, glow_radius * 2, glow_color, glow_intensity * 0.4)
            # Medium glow
            draw_circle_additive(canvas, x, y, glow_radius, glow_color, glow_intensity * 0.6)

        # Agent body
        draw_circle(canvas, x, y, agent['size'], agent['base_color'], 0.9)

    # 6. Visitor indicators - white aura (similar to tree aura but lighter)
    for visitor in render_data.get('visitors', []):
        x, y = int(visitor['x']), int(visitor['y'])
        # White aura with soft glow layers
        white_color = (255, 255, 255)
        radius = 60  # Base radius for visitor aura
        # Outer soft glow
        draw_circle_additive(canvas, x, y, radius * 2.5, white_color, 0.15)
        # Middle glow
        draw_circle_additive(canvas, x, y, radius * 1.5, white_color, 0.25)
        # Inner core
        draw_circle_additive(canvas, x, y, radius, white_color, 0.35)

    # 7. Pollination dances (spiral effect at edge of trees)
    for dance in render_data.get('dances', []):
        for particle in dance.get('particles', []):
            x, y = int(particle['x']), int(particle['y'])
            color = particle['color']
            alpha = particle['alpha']
            size = int(particle['size'])

            # Larger glow layers for more visible spiral
            draw_circle_additive(canvas, x, y, size * 3, color, alpha * 0.3)
            draw_circle_additive(canvas, x, y, size * 2, color, alpha * 0.5)
            draw_circle_additive(canvas, x, y, size, color, alpha * 0.8)

    scriptOp.copyNumpyArray(canvas)

def draw_circle(canvas, x, y, radius, color, alpha):
    """Draw filled circle with alpha blending."""
    if radius <= 0 or alpha <= 0:
        return

    height, width = canvas.shape[:2]
    x, y, radius = int(x), int(y), int(radius)

    x_min = max(0, x - radius)
    x_max = min(width, x + radius + 1)
    y_min = max(0, y - radius)
    y_max = min(height, y + radius + 1)

    if x_min >= x_max or y_min >= y_max:
        return

    yy, xx = np.ogrid[y_min:y_max, x_min:x_max]
    mask = (xx - x)**2 + (yy - y)**2 <= radius**2

    if mask.any():
        r, g, b = color[0] / 255.0, color[1] / 255.0, color[2] / 255.0
        # Alpha blending
        canvas[y_min:y_max, x_min:x_max, 0][mask] = r * alpha + canvas[y_min:y_max, x_min:x_max, 0][mask] * (1 - alpha)
        canvas[y_min:y_max, x_min:x_max, 1][mask] = g * alpha + canvas[y_min:y_max, x_min:x_max, 1][mask] * (1 - alpha)
        canvas[y_min:y_max, x_min:x_max, 2][mask] = b * alpha + canvas[y_min:y_max, x_min:x_max, 2][mask] * (1 - alpha)

def draw_circle_additive(canvas, x, y, radius, color, alpha):
    """Draw circle with additive blending (for glows)."""
    if radius <= 0 or alpha <= 0:
        return

    height, width = canvas.shape[:2]
    x, y, radius = int(x), int(y), int(radius)

    x_min = max(0, x - radius)
    x_max = min(width, x + radius + 1)
    y_min = max(0, y - radius)
    y_max = min(height, y + radius + 1)

    if x_min >= x_max or y_min >= y_max:
        return

    yy, xx = np.ogrid[y_min:y_max, x_min:x_max]
    mask = (xx - x)**2 + (yy - y)**2 <= radius**2

    if mask.any():
        r, g, b = color[0] / 255.0, color[1] / 255.0, color[2] / 255.0
        # Additive blending (clamped to 1.0)
        canvas[y_min:y_max, x_min:x_max, 0][mask] = np.minimum(1.0, canvas[y_min:y_max, x_min:x_max, 0][mask] + r * alpha)
        canvas[y_min:y_max, x_min:x_max, 1][mask] = np.minimum(1.0, canvas[y_min:y_max, x_min:x_max, 1][mask] + g * alpha)
        canvas[y_min:y_max, x_min:x_max, 2][mask] = np.minimum(1.0, canvas[y_min:y_max, x_min:x_max, 2][mask] + b * alpha)

def draw_circle_ring(canvas, x, y, outer_radius, inner_radius, color, alpha):
    """Draw a ring (hollow circle)."""
    if outer_radius <= 0 or alpha <= 0:
        return

    height, width = canvas.shape[:2]
    x, y = int(x), int(y)
    outer_radius, inner_radius = int(outer_radius), int(inner_radius)

    x_min = max(0, x - outer_radius)
    x_max = min(width, x + outer_radius + 1)
    y_min = max(0, y - outer_radius)
    y_max = min(height, y + outer_radius + 1)

    if x_min >= x_max or y_min >= y_max:
        return

    yy, xx = np.ogrid[y_min:y_max, x_min:x_max]
    dist_sq = (xx - x)**2 + (yy - y)**2
    mask = (dist_sq <= outer_radius**2) & (dist_sq >= inner_radius**2)

    if mask.any():
        r, g, b = color[0] / 255.0, color[1] / 255.0, color[2] / 255.0
        canvas[y_min:y_max, x_min:x_max, 0][mask] = r * alpha + canvas[y_min:y_max, x_min:x_max, 0][mask] * (1 - alpha)
        canvas[y_min:y_max, x_min:x_max, 1][mask] = g * alpha + canvas[y_min:y_max, x_min:x_max, 1][mask] * (1 - alpha)
        canvas[y_min:y_max, x_min:x_max, 2][mask] = b * alpha + canvas[y_min:y_max, x_min:x_max, 2][mask] * (1 - alpha)

def onSetupParameters(scriptOp):
    return

def onPulse(par):
    return
