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

    # Get structure positions for mycelial network
    structures = render_data.get('structures', [])

    # === BACKGROUND EFFECTS ===

    # 0a. Subtle watery ripples throughout the space
    num_ripple_centers = 8  # Number of ripple origin points
    for ripple_idx in range(num_ripple_centers):
        # Deterministic ripple positions spread across canvas
        seed = ripple_idx * 7919  # Prime for good distribution
        ripple_x = ((seed * 31337) % width)
        ripple_y = ((seed * 17389) % height)

        # Multiple expanding rings per center
        for ring in range(3):
            # Each ring expands outward over time, then resets
            cycle_time = 8.0 + ripple_idx * 0.5  # Seconds per cycle
            ring_offset = ring * (cycle_time / 3)  # Stagger rings
            t = ((flow_time + ring_offset) % cycle_time) / cycle_time

            # Ripple expands from 0 to max_radius
            max_radius = 200 + ripple_idx * 30
            current_radius = t * max_radius

            # Fade in then out (peak at 0.3 of cycle) - brighter now
            if t < 0.3:
                alpha = t / 0.3 * 0.18
            else:
                alpha = (1.0 - (t - 0.3) / 0.7) * 0.18

            # Brighter blue-green tint
            ripple_color = (70, 100, 115)
            ring_width = 15 + ring * 5

            if current_radius > ring_width:
                draw_circle_ring_soft(canvas, ripple_x, ripple_y,
                                     int(current_radius), int(current_radius - ring_width),
                                     ripple_color, alpha)

    # 0b. Mycelial network - pulses flowing between trees
    if len(structures) >= 2:
        # Create connections between all tree pairs
        mycelial_color = (100, 75, 130)  # Brighter purple

        for i in range(len(structures)):
            for j in range(i + 1, len(structures)):
                s1 = structures[i]
                s2 = structures[j]
                x1, y1 = int(s1['x']), int(s1['y'])
                x2, y2 = int(s2['x']), int(s2['y'])

                # Draw multiple pulses traveling along the connection
                num_pulses = 3
                for pulse_idx in range(num_pulses):
                    # Each pulse travels from one tree to the other
                    pulse_speed = 0.15 + pulse_idx * 0.05  # Different speeds
                    pulse_offset = pulse_idx * 0.33  # Stagger pulses

                    # Bidirectional - some go one way, some the other
                    if pulse_idx % 2 == 0:
                        t = ((flow_time * pulse_speed + pulse_offset) % 1.0)
                    else:
                        t = 1.0 - ((flow_time * pulse_speed + pulse_offset) % 1.0)

                    # Pulse position along the line
                    px = x1 + (x2 - x1) * t
                    py = y1 + (y2 - y1) * t

                    # Add organic waviness to path
                    wave_offset = math.sin(t * math.pi * 4 + flow_time + i + j) * 25
                    dx, dy = x2 - x1, y2 - y1
                    length = math.sqrt(dx*dx + dy*dy)
                    if length > 0:
                        # Perpendicular offset
                        px += (-dy / length) * wave_offset
                        py += (dx / length) * wave_offset

                    # Pulse intensity (brightest in middle of journey) - brighter now
                    pulse_alpha = math.sin(t * math.pi) * 0.45

                    # Draw pulse as soft glow
                    pulse_radius = 30 + math.sin(flow_time * 3 + pulse_idx) * 10
                    draw_circle_additive(canvas, int(px), int(py), int(pulse_radius * 2), mycelial_color, pulse_alpha * 0.3)
                    draw_circle_additive(canvas, int(px), int(py), int(pulse_radius), mycelial_color, pulse_alpha * 0.5)
                    draw_circle_additive(canvas, int(px), int(py), int(pulse_radius * 0.5), mycelial_color, pulse_alpha)

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

    # 3. Visitor trails (particle effect!)
    for trail_idx, trail_points in enumerate(render_data.get('visitor_trails', [])):
        for point_idx, point in enumerate(trail_points):
            base_x = point['x']
            base_y = point['y']
            color = point['color']
            alpha = point['alpha']
            size = int(point['size'])

            # Spawn multiple particles around each trail point
            num_particles = 5 + int(alpha * 4)  # More particles when brighter
            for p_idx in range(num_particles):
                # Deterministic but animated particle positions
                seed = trail_idx * 10000 + point_idx * 100 + p_idx
                particle_angle = (seed * 2.399) + flow_time * (0.5 + (seed % 10) * 0.1)  # Golden angle + rotation
                particle_dist = 8 + (seed % 20) + math.sin(flow_time * 2 + seed) * 6

                # Particles drift outward as trail fades
                drift = (1.0 - alpha) * 15
                particle_dist += drift

                # Calculate particle position
                px = int(base_x + math.cos(particle_angle) * particle_dist)
                py = int(base_y + math.sin(particle_angle) * particle_dist)

                # Particle size and alpha vary
                p_size = max(2, size * (0.3 + (seed % 5) * 0.15))
                p_alpha = alpha * (0.4 + (seed % 10) * 0.06) * (0.7 + math.sin(flow_time * 3 + seed) * 0.3)

                # Draw particle with glow
                draw_circle_additive(canvas, px, py, int(p_size * 2), color, p_alpha * 0.4)
                draw_circle_additive(canvas, px, py, int(p_size), color, p_alpha * 0.7)

            # Still draw core trail point (smaller now, particles are the main effect)
            wave1 = math.sin((base_x * 0.02) + (flow_time * 2) + (trail_idx * 0.5)) * 8
            wave2 = math.cos((base_y * 0.014) + (flow_time * 1.5) + (point_idx * 0.1)) * 5
            x = int(base_x + wave1)
            y = int(base_y + wave2)
            draw_circle_additive(canvas, x, y, size * 2, color, alpha * 0.5)
            draw_circle_additive(canvas, x, y, size, color, alpha * 0.8)

    # 4. Visitor auras (color from touching trees) - particle cloud
    for aura_idx, aura in enumerate(render_data.get('visitor_auras', [])):
        if aura is not None:
            x, y = int(aura['x']), int(aura['y'])
            color = aura['color']
            intensity = aura['intensity']
            radius = int(aura['glow_radius'] * aura['pulse'] * 8)  # 2x larger radius

            # Particle cloud instead of solid circles
            num_particles = 80

            for i in range(num_particles):
                seed = aura_idx * 5000 + i + 50000  # Offset to differ from trees

                # Golden angle distribution
                golden_angle = math.pi * (3 - math.sqrt(5))
                theta_base = i * golden_angle
                r_base = math.sqrt((i + 0.5) / num_particles) * radius * 0.9

                # Floating animation
                float_speed = 0.4 + (seed % 100) / 250.0
                float_amp = 8 + (seed % 20)  # Smaller amplitude than trees

                # Orbital drift
                theta = theta_base + math.sin(flow_time * float_speed + seed) * 0.25
                r = r_base + math.sin(flow_time * float_speed * 0.7 + seed * 0.1) * float_amp

                # Particle position
                px = int(x + math.cos(theta) * r)
                py = int(y + math.sin(theta) * r)

                # Smaller particle size than trees
                particle_size = 6 + (seed % 6)

                # Alpha varies by distance and time
                dist_factor = 1.0 - (r / max(radius, 1)) * 0.3
                pulse = 0.7 + math.sin(flow_time * 2.5 + seed * 0.5) * 0.3
                p_alpha = intensity * 0.7 * dist_factor * pulse

                # Draw particle with glow
                draw_circle_additive(canvas, px, py, int(particle_size * 2), color, p_alpha * 0.4)
                draw_circle_additive(canvas, px, py, int(particle_size * 1.3), color, p_alpha * 0.6)
                draw_circle_additive(canvas, px, py, int(particle_size), color, p_alpha * 0.8)

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

    # 6. Visitor indicators - white particle cloud (only if not carrying color)
    visitor_auras = render_data.get('visitor_auras', [])
    for visitor_idx, visitor in enumerate(render_data.get('visitors', [])):
        # Check if this visitor has a colored aura
        has_color = False
        if visitor_idx < len(visitor_auras):
            aura = visitor_auras[visitor_idx]
            if aura is not None and aura.get('intensity', 0) > 0.05:
                has_color = True

        # Only show white aura if not carrying a color
        if has_color:
            continue

        x, y = int(visitor['x']), int(visitor['y'])
        white_color = (255, 255, 255)
        radius = 120  # 2x larger radius

        # Particle cloud
        num_particles = 80

        for i in range(num_particles):
            seed = visitor_idx * 3000 + i + 80000  # Unique offset

            # Golden angle distribution
            golden_angle = math.pi * (3 - math.sqrt(5))
            theta_base = i * golden_angle
            r_base = math.sqrt((i + 0.5) / num_particles) * radius * 0.85

            # Floating animation
            float_speed = 0.5 + (seed % 100) / 300.0
            float_amp = 6 + (seed % 15)

            # Orbital drift
            theta = theta_base + math.sin(flow_time * float_speed + seed) * 0.2
            r = r_base + math.sin(flow_time * float_speed * 0.8 + seed * 0.1) * float_amp

            # Particle position
            px = int(x + math.cos(theta) * r)
            py = int(y + math.sin(theta) * r)

            # Smaller particle size
            particle_size = 5 + (seed % 5)

            # Alpha varies by distance and time
            dist_factor = 1.0 - (r / max(radius, 1)) * 0.25
            pulse = 0.75 + math.sin(flow_time * 2.2 + seed * 0.4) * 0.25
            p_alpha = 0.35 * dist_factor * pulse

            # Draw particle with glow
            draw_circle_additive(canvas, px, py, int(particle_size * 2), white_color, p_alpha * 0.4)
            draw_circle_additive(canvas, px, py, int(particle_size * 1.3), white_color, p_alpha * 0.6)
            draw_circle_additive(canvas, px, py, int(particle_size), white_color, p_alpha * 0.8)

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

def draw_circle_ring_soft(canvas, x, y, outer_radius, inner_radius, color, alpha):
    """Draw a soft ring with additive blending and gradient falloff (for ripples)."""
    if outer_radius <= 0 or alpha <= 0:
        return

    height, width = canvas.shape[:2]
    x, y = int(x), int(y)
    outer_radius, inner_radius = int(outer_radius), max(0, int(inner_radius))

    x_min = max(0, x - outer_radius)
    x_max = min(width, x + outer_radius + 1)
    y_min = max(0, y - outer_radius)
    y_max = min(height, y + outer_radius + 1)

    if x_min >= x_max or y_min >= y_max:
        return

    yy, xx = np.ogrid[y_min:y_max, x_min:x_max]
    dist = np.sqrt((xx - x)**2 + (yy - y)**2)

    # Create soft falloff within the ring
    ring_center = (outer_radius + inner_radius) / 2
    ring_width = (outer_radius - inner_radius) / 2

    if ring_width <= 0:
        return

    # Distance from ring center (0 at center of ring, 1 at edges)
    ring_dist = np.abs(dist - ring_center) / ring_width
    # Soft falloff - strongest at ring center
    falloff = np.maximum(0, 1 - ring_dist)
    # Only apply within the ring bounds (with some feathering)
    mask = dist <= outer_radius

    if mask.any():
        r, g, b = color[0] / 255.0, color[1] / 255.0, color[2] / 255.0
        intensity = falloff * alpha
        # Additive blending for subtle glow
        canvas[y_min:y_max, x_min:x_max, 0][mask] = np.minimum(1.0, canvas[y_min:y_max, x_min:x_max, 0][mask] + r * intensity[mask])
        canvas[y_min:y_max, x_min:x_max, 1][mask] = np.minimum(1.0, canvas[y_min:y_max, x_min:x_max, 1][mask] + g * intensity[mask])
        canvas[y_min:y_max, x_min:x_max, 2][mask] = np.minimum(1.0, canvas[y_min:y_max, x_min:x_max, 2][mask] + b * intensity[mask])

def onSetupParameters(scriptOp):
    return

def onPulse(par):
    return
