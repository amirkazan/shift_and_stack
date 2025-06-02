from typing import Any, List, Tuple

import numpy as np
from scipy.ndimage import shift

from .detection import detect_candidates


def shift_and_stack_numpy(images: List[np.ndarray], vx: float, vy: float)\
        -> np.ndarray:
    stacked = np.zeros_like(images[0], dtype=np.float32)
    for k, frame in enumerate(images):
        dx = -k * vx
        dy = -k * vy
        shifted = shift(frame, shift=(dy, dx), order=1, mode='constant',
                        cval=0.0)
        stacked += shifted
    return stacked


def evaluate_all_hypotheses(
    images: List[np.ndarray],
    velocity_grid: List[Tuple[float, float]],
    sigma
) -> tuple[list[Any], list[Any]]:
    results = []
    stack = []
    for vx, vy in velocity_grid:
        stacked = shift_and_stack_numpy(images, vx, vy)
        candidates = detect_candidates(stacked, vx, vy, threshold_sigma=sigma)
        results.append(candidates)
        if candidates:
            stack.append(stacked)

    return results, stack
