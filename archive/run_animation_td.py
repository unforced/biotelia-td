"""
Run this script inside TouchDesigner to animate the pollination system.

To use:
1. In TouchDesigner, open the Textport (Alt+T)
2. Type: run("/Users/unforced/Symbols/Codes/biotelia-td/run_animation_td.py")
3. Press Enter
4. Watch /project1/gpu_renderer/OUT while it runs

Or create a Text DAT, paste this code in, and press Ctrl+R
"""

import time

def animate(duration_seconds=30):
    """Animate the pollination system for the specified duration."""

    exporter = op('/project1/hybrid_data_exporter')
    circles = op('/project1/gpu_renderer/optimized_circles')
    poll_sys = op('/project1/pollination_system')
    position_chop = op('/project1/input_switch')

    print(f"Starting {duration_seconds} second animation...")
    print("Watch /project1/gpu_renderer/OUT")
    print("Pollinators should be moving around!")
    print("")

    frames = int(duration_seconds * 60)

    for frame in range(frames):
        # Update system
        poll_sys.module.update_frame(position_chop, 1.0/60.0)
        exporter.module.update_and_export()
        circles.cook(force=True)

        # Progress indicator
        if frame % 60 == 0:
            elapsed = frame / 60
            print(f"  {elapsed:.0f}/{duration_seconds} seconds...")

        # 60 FPS timing
        time.sleep(1.0/60.0)

    print(f"\n✓ Animation complete! Ran {frames} frames at 60 FPS")

# Run 30 seconds of animation by default
if __name__ == "__main__":
    animate(30)
