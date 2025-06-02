import re

import numpy as np
from astropy.io.fits import Header
from astropy.wcs import WCS


def compute_focal_length(aperture_diameter_m, fov_x_deg, fov_y_deg):
    fov_x_rad = np.deg2rad(fov_x_deg)
    fov_y_rad = np.deg2rad(fov_y_deg)
    tan_x = np.tan(fov_x_rad / 2)
    tan_y = np.tan(fov_y_rad / 2)
    scale = np.sqrt(tan_x**2 + tan_y**2)
    focal_m = aperture_diameter_m / (2 * scale)
    return focal_m * 1000  # мм


def compute_pixels_per_arcsec(pixel_size_um, focal_length_mm):
    px_size_m = pixel_size_um * 1e-6
    focal_m = focal_length_mm * 1e-3
    theta_rad = px_size_m / focal_m
    theta_arcsec = theta_rad * 206265.0
    return 1.0 / theta_arcsec


def get_observation_parameters(
    header: Header,
    aperture_diameter_m: float,
    fov_x_deg: float,
    fov_y_deg: float
) -> dict:
    time_step = float(header.get("EXPTIME", 1.0))  # сек

    pxsize_str = header.get("PXSIZE", "25.0 x 25.0")
    match = re.search(r"([\d\.]+)", pxsize_str)
    pixel_size_um = float(match.group(1)) if match else 25.0

    focal_mm = compute_focal_length(aperture_diameter_m, fov_x_deg, fov_y_deg)
    pixels_per_arcsec = compute_pixels_per_arcsec(pixel_size_um, focal_mm)

    return {
        "time_step": time_step,
        "pixels_per_arcsec": pixels_per_arcsec
    }


def create_simple_wcs(image_shape, fov_x_deg, fov_y_deg, ra_center_deg,
                      dec_center_deg):
    ny, nx = image_shape
    w = WCS(naxis=2)
    w.wcs.crpix = [nx / 2, ny / 2]
    w.wcs.cdelt = [-fov_x_deg / nx, fov_y_deg / ny]
    w.wcs.crval = [ra_center_deg, dec_center_deg]
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    return w
