from typing import Any

import astropy.units as u
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
from sklearn.cluster import DBSCAN


def deduplicate_candidates(candidates: list[dict], xy_eps: float = 3.0)\
        -> list[dict]:

    if not candidates:
        return []

    coords = np.array([[c['x'], c['y']] for c in candidates])
    clustering = DBSCAN(eps=xy_eps, min_samples=1).fit(coords)
    labels = clustering.labels_

    deduplicated = []
    for label in set(labels):
        group = [candidates[i] for i in range(len(candidates))
                 if labels[i] == label]
        # выбираем объект с максимальным сигналом
        best = max(group, key=lambda c: c['signal'])

        # усреднение координат и скоростей
        avg_x = np.mean([g['x'] for g in group])
        avg_y = np.mean([g['y'] for g in group])
        avg_vx = np.mean([g['vx'] for g in group])
        avg_vy = np.mean([g['vy'] for g in group])

        deduplicated.append({
            'x': avg_x,
            'y': avg_y,
            'vx': avg_vx,
            'vy': avg_vy,
            'signal': best['signal'],
            'snr': best['snr'],
            'x0': best['x0'],
            'y0': best['y0']
        })

    return deduplicated


def is_track_on_star(
        candidate, stars: SkyCoord, wcs_transform,
        num_frames: int, radius_arcsec: float = 5.0):
    x0, y0 = candidate['x0'], candidate['y0']
    vx, vy = candidate['vx'], candidate['vy']

    coords = []
    for k in range(num_frames):
        xk = x0 + k * vx
        yk = y0 + k * vy
        ra_k, dec_k = wcs_transform(xk, yk)
        coords.append(SkyCoord(ra=ra_k * u.rad, dec=dec_k * u.rad))

    # проверяем, попадает ли хотя бы одна точка на звезду
    for coord in coords:
        sep = coord.separation(stars)
        if np.any(sep.arcsec < radius_arcsec):
            return True  # трек проходит через звезду
    return False


def remove_stationary_sources(
        candidates: list[dict], star_catalog_csv: str,
        wcs_transform, image_width, wcs,
        radius_arcsec: float = 5.0) -> tuple[list[Any], SkyCoord]:
    catalog = pd.read_csv(star_catalog_csv)
    if {'ra_rad', 'dec_rad'}.issubset(catalog.columns):
        ra = catalog['ra_rad'].values
        dec = catalog['dec_rad'].values
    elif {'RightAscension', 'Declination'}.issubset(catalog.columns):
        ra = catalog["RightAscension"].values
        dec = catalog["Declination"].values
    stars = SkyCoord(ra=ra * u.rad, dec=dec * u.rad)
    star_x, star_y = wcs.world_to_pixel(stars)
    corrected_star_x = image_width - star_x  # отразим горизонтально
    ra, dec = wcs_transform(corrected_star_x, star_y)
    stars = SkyCoord(ra=ra * u.rad, dec=dec * u.rad)

    filtered = []
    for obj in candidates:
        if is_track_on_star(obj, stars, wcs_transform, num_frames=50,
                            radius_arcsec=radius_arcsec):
            continue
        ra, dec = wcs_transform(obj['x0'], obj['y0'])  # преобразование коорд.
        candidate_coord = SkyCoord(ra=ra * u.rad, dec=dec * u.rad)
        sep = candidate_coord.separation(stars)

        if np.all(sep.arcsec > radius_arcsec):
            obj['ra'] = float(ra)
            obj['dec'] = float(dec)
            filtered.append(obj)

    return filtered, stars
