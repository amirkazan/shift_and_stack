import numpy as np
from scipy.ndimage import center_of_mass, label, maximum_filter


def detect_candidates(
    stacked_image: np.ndarray,
    vx: float,
    vy: float,
    threshold_sigma: float = 5.0,
) -> list[dict]:
    background = np.median(stacked_image)
    noise = np.std(stacked_image)
    threshold = background + threshold_sigma * noise

    # локальные максимумы
    neighborhood = maximum_filter(stacked_image, size=3)
    local_max = (stacked_image == neighborhood) & (stacked_image > threshold)

    labeled, num_features = label(local_max)
    coms = center_of_mass(stacked_image, labeled, range(1, num_features + 1))

    results = []

    for y, x in coms:
        if not (0 <= x < stacked_image.shape[1] and
                0 <= y < stacked_image.shape[0]):
            continue
        x0 = x - vx
        y0 = y - vy
        signal = stacked_image[int(round(y)), int(round(x))]
        snr = (signal - background) / (noise + 1e-6)
        results.append({
            'x': float(x),
            'y': float(y),
            'vx': float(vx),
            'vy': float(vy),
            'signal': float(signal),
            'snr': float(snr),
            'x0': float(x0),
            'y0': float(y0),
        })

    return results
