# Improved rendering with better trail visibility
import numpy as np

def onCook(scriptOp):
    """Render pollination system with enhanced trail visibility."""

    pollination_dat = op('/project1/pollination_system')
    input_chop = op('/project1/scale_to_canvas')

    if not pollination_dat:
        scriptOp.copyNumpyArray(np.zeros((1280, 1280, 4), dtype=np.float32))
        return

    try:
        render_data = pollination_dat.module.update_frame(input_chop, 1.0/60.0)
    except Exception as e:
        scriptOp.copyNumpyArray(np.zeros((1280, 1280, 4), dtype=np.float32))
        return

    # Create canvas
    canvas = np.zeros((1280, 1280, 4), dtype=np.float32)

    # Background (dark forest floor)
    canvas[:, :, 0] = 10 / 255.0
    canvas[:, :, 1] = 15 / 255.0
    canvas[:, :, 2] = 8 / 255.0
    canvas[:, :, 3] = 1.0

    # === RENDER LAYERS ===

    # 1. Structures (trees)
    for structure in render_data.get('structures', []):
        x, y = int(structure['x']), int(structure['y'])
        radius = int(structure['radius'] * structure['pulse'])
        color = structure['color']

        # Outer glow
        draw_circle_additive(canvas, x, y, radius * 1.8, color, 0.15)
        # Structure body
        draw_circle(canvas, x, y, radius, color, 0.9)
        # Core
        draw_circle(canvas, x, y, 12, color, 1.0)

    # 2. Agent trails (with actual colors!)
    for agent in render_data.get('agents', []):
        for point in agent.get('trail', []):
            x, y = int(point['x']), int(point['y'])
            color = point['color']
            alpha = point['alpha']
            size = int(point['size'])

            # Make trails MUCH more visible
            # Glow
            draw_circle_additive(canvas, x, y, size * 3, color, alpha * 0.5)
            # Core
            draw_circle_additive(canvas, x, y, size, color, alpha * 0.8)

    # 3. Visitor trails
    for trail_points in render_data.get('visitor_trails', []):
        for point in trail_points:
            x, y = int(point['x']), int(point['y'])
            color = point['color']
            alpha = point['alpha']
            size = int(point['size'])

            # Glow
            draw_circle_additive(canvas, x, y, size * 3, color, alpha * 0.5)
            # Core
            draw_circle_additive(canvas, x, y, size, color, alpha * 0.8)

    # 4. Visitor auras (color-changing!)
    for aura in render_data.get('visitor_auras', []):
        if aura is not None:
            x, y = int(aura['x']), int(aura['y'])
            color = aura['color']
            intensity = aura['intensity']
            radius = int(aura['glow_radius'] * aura['pulse'])

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

    # 6. Visitor indicators
    for visitor in render_data.get('visitors', []):
        x, y = int(visitor['x']), int(visitor['y'])
        # Yellow ring
        draw_circle_ring(canvas, x, y, 14, 12, (255, 230, 100), 0.8)

    # 7. Pollination dances
    for dance in render_data.get('dances', []):
        for particle in dance.get('particles', []):
            x, y = int(particle['x']), int(particle['y'])
            color = particle['color']
            alpha = particle['alpha']
            size = int(particle['size'])

            draw_circle_additive(canvas, x, y, size * 2, color, alpha * 0.6)
            draw_circle_additive(canvas, x, y, size, color, alpha)

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
