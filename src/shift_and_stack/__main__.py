import argparse
from pathlib import Path

import numpy as np

from .compute_parameters import create_simple_wcs, get_observation_parameters
from .filtering import deduplicate_candidates, remove_stationary_sources
from .hypothesis import generate_velocity_grid
from .load_config import load_config
from .load_files import load_fits_series
from .preprocess import preprocess_image_optional
from .results import form_detection_results
from .shift_and_stack import evaluate_all_hypotheses
from .visualize import visualize_detections_with_catalog_and_truth

PROJECT_ROOT = Path(__file__).parent.parent.parent


def parse_args():
    parser = argparse.ArgumentParser(description='Process astronomical'
                                                 'images for moving object'
                                                 'detection')
    parser.add_argument(
        '--config',
        type=str,
        default=f'{Path(__file__).parent.parent.parent}/example/config.yml',
        help='Path to configuration YAML file'
    )
    return parser.parse_args()


def main(config_path: str):
    config = load_config(config_path)

    x_angular_deg = config.x_angular_deg
    y_angular_deg = config.y_angular_deg
    front_aperture = config.front_aperture
    sigma = config.sigma
    path_to_fits = f"{PROJECT_ROOT}/{config.paths.fits}"

    images, header = load_fits_series(path_to_fits)
    obs_params = get_observation_parameters(header, front_aperture,
                                            x_angular_deg, y_angular_deg)
    time_step = obs_params['time_step']
    pixels_per_arcsec = obs_params['pixels_per_arcsec']

    grid = generate_velocity_grid(
        mode=config.grid.mode,
        angle_steps=config.grid.angle_steps,
        speed_steps=config.grid.speed_steps,
        max_speed_arcsec=config.grid.max_speed_arcsec,
        dt=time_step,
        pixels_per_arcsec=pixels_per_arcsec,
        min_speed=config.grid.min_speed,
    )

    preprocessed_images = []
    for image in images:
        preprocessed_images.append(preprocess_image_optional(image, 'light'))

    candidates, stacked = evaluate_all_hypotheses(preprocessed_images,
                                                  grid, sigma)
    flat_candidates = [c for group in candidates for c in group]
    result = deduplicate_candidates(flat_candidates, 5.0)

    wcs = create_simple_wcs(
        image_shape=config.wcs.image_shape,
        fov_x_deg=config.wcs.fov_x_deg,
        fov_y_deg=config.wcs.fov_y_deg,
        ra_center_deg=config.wcs.ra_center_deg,
        dec_center_deg=config.wcs.dec_center_deg
    )

    def wcs_transform(x, y):
        ra_deg, dec_deg = wcs.all_pix2world(x, y, 0)
        return np.deg2rad(ra_deg), np.deg2rad(dec_deg)

    result, stars = remove_stationary_sources(
        result, path_to_fits+'/frame_0_stars.csv', wcs_transform,
        preprocessed_images[0].shape[1], wcs, 30.0)

    results = form_detection_results(result, 0.0)
    visualize_detections_with_catalog_and_truth(preprocess_image_optional(
        images[0], 'heavy'), result, path_to_fits+'/frame_0_stars.csv',
        path_to_fits+'/frame_0_objects.csv', wcs)

    for i, r in enumerate(results):
        print(f"{i+1})RA={r['ra']:.5f}, Dec={r['dec']:.5f}, "
              f"Mag={r['mag']:.2f}, "
              f"ω={r['omega']:.3f}, φ={np.degrees(r['phi']):.1f}°, t="
              f"{r['time']}\n")


if __name__ == '__main__':
    args = parse_args()
    main(args.config)
