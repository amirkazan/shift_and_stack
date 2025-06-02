from dataclasses import dataclass
from typing import List

import yaml


@dataclass
class PathsConfig:
    fits: str
    stars: str


@dataclass
class GridConfig:
    mode: str
    angle_steps: int
    speed_steps: int
    max_speed_arcsec: float
    min_speed: float


@dataclass
class WCSConfig:
    image_shape: List[int]
    fov_x_deg: float
    fov_y_deg: float
    ra_center_deg: float
    dec_center_deg: float


@dataclass
class AppConfig:
    x_angular_deg: float
    y_angular_deg: float
    front_aperture: float
    sigma: float
    paths: PathsConfig
    grid: GridConfig
    wcs: WCSConfig


def load_config(config_path: str) -> AppConfig:
    with open(config_path) as f:
        raw = yaml.safe_load(f)
    return AppConfig(
        x_angular_deg=raw['x_angular_deg'],
        y_angular_deg=raw['y_angular_deg'],
        front_aperture=raw['front_aperture'],
        sigma=raw['sigma'],
        paths=PathsConfig(**raw['paths']),
        grid=GridConfig(**raw['grid']),
        wcs=WCSConfig(**raw['wcs'])
    )
