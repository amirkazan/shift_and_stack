import os

import numpy as np
from astropy.io import fits


def load_fits_series(folder_path):
    fits_files = sorted([
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith('.fits')
    ])

    if not fits_files:
        raise ValueError(f"Нет FITS-файлов в папке: {folder_path}")

    images = []
    header = None

    for idx, file_path in enumerate(fits_files):
        with fits.open(file_path) as hdul:
            img = hdul[0].data.astype(np.float32)
            images.append(img)
            if idx == 0:
                header = hdul[0].header

    return images, header
