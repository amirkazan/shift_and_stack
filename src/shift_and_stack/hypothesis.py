import numpy as np


def generate_velocity_grid(
    mode: str,
    *,
    angle_steps: int = None,
    speed_steps: int = None,
    max_speed_arcsec: float = None,
    dt: float = None,
    pixels_per_arcsec: float = None,
    max_shift_px: float = None,
    delta_px: float = None,
    min_speed
) -> list[tuple[float, float]]:

    velocities = []

    if mode == 'polar':
        assert None not in (
            angle_steps, speed_steps, max_speed_arcsec, dt, pixels_per_arcsec
        ), "Не хватает параметров для режима 'polar'"

        angles = np.append(np.linspace(0, 2 * np.pi, angle_steps,
                                       endpoint=True), 0.)
        speeds_arcsec = np.linspace(min_speed, max_speed_arcsec, speed_steps)
        for angle in angles:
            for speed in speeds_arcsec:
                speed_px = speed * pixels_per_arcsec * dt
                vx = speed_px * np.cos(angle)
                vy = speed_px * np.sin(angle)
                velocities.append((vx, vy))
    elif mode == 'cartesian':
        assert None not in (max_shift_px, delta_px), \
            "Не хватает параметров для режима 'cartesian'"

        v_range = np.arange(-max_shift_px, max_shift_px + 1e-6, delta_px)
        for vx in v_range:
            for vy in v_range:
                velocities.append((vx, vy))
    else:
        raise ValueError("mode должен быть 'polar' или 'cartesian'")

    return velocities
