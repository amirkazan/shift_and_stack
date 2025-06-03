# Shift and Stack: Detection of Moving Objects in Astronomical Images

**Shift and Stack** is a Python script for detecting moving objects in series of astronomical images using the shift-and-stack algorithm.

## Key Features

-  Efficient detection of moving objects in FITS image sequences
-  Support for different velocity grids (polar and cartesian)
-  Built-in preprocessing and candidate filtering
-  Visualization tools for result verification

## Installation

### Prerequisites
- Python 3.12+
- Poetry (for dependency management)

### Install with Poetry
```bash
git clone https://github.com/amirkazan/shift_and_stack.git
cd shift_and_stack
poetry install
```

## Usage

### Command Line Interface

```bash
python -m src.shift_and_stack.__main__ --config example/config.yml
```

## Configuration

Create a YAML configuration file:

```yaml
# config.yml
x_angular_deg: 2.0
y_angular_deg: 2.0
front_aperture: 1
sigma: 7.0

paths:
  fits: "data/fits_series"
  stars: "data/stars/tycho_catalog.csv"

grid:
  mode: "polar"
  angle_steps: 36
  speed_steps: 10
  max_speed_arcsec: 2.0
  min_speed: 0.3

wcs:
  image_shape: [2048, 2048]
  fov_x_deg: 2.0
  fov_y_deg: 2.0
  ra_center_deg: 180.0
  dec_center_deg: 30.0
```

## Contact

For questions or suggestions, please contact:
- GitHub: [@amirkazan](https://github.com/amirkazan)
