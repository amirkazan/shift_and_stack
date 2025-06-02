import cv2
import numpy as np
from astropy.stats import sigma_clip
from numpy import ma


def preprocess_image_optional(image: np.ndarray, mode: str = "heavy")\
        -> np.ndarray:

    assert mode in ("light", "heavy")

    image = np.nan_to_num(image.astype(np.float32), nan=0.0, posinf=0.0,
                          neginf=0.0)
    ny, nx = image.shape

    blur1 = int(np.clip(min(ny, nx) * 0.01, 11, 31))
    blur2 = int(np.clip(min(ny, nx) * 0.03, 21, 81))
    if blur1 % 2 == 0:
        blur1 += 1
    if blur2 % 2 == 0:
        blur2 += 1

    if mode == "light":
        # более слабое сглаживание
        background = cv2.GaussianBlur(image, (blur2, blur2), sigmaX=1.0)
    else:
        bg_stage1 = cv2.GaussianBlur(image, (blur1, blur1), sigmaX=1.0)
        background = cv2.GaussianBlur(bg_stage1, (blur2, blur2), sigmaX=2.0)

    img_bg_sub = image - background
    # sigma-клиппинг
    sigma_val = 4.0 if mode == "light" else np.clip(np.std(img_bg_sub) / 10,
                                                    2.0, 5.0)
    clipped = sigma_clip(img_bg_sub, sigma=sigma_val, maxiters=5)
    img_clean = ma.filled(clipped, fill_value=np.median(img_bg_sub))

    # нормализация
    mean = np.mean(img_clean)
    std = np.std(img_clean)
    img_norm = (img_clean - mean) / std if std > 0 else img_clean

    if mode == "heavy":
        ksize = int(np.clip(min(ny, nx) / 300, 3, 7))
        if ksize % 2 == 0:
            ksize += 1
        img_final = cv2.GaussianBlur(img_norm, (ksize, ksize), sigmaX=0.6)
        img_final = -1 * img_final
    else:
        img_final = img_norm
        img_final = -1 * img_final

    return img_final
