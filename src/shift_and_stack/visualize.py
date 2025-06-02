import astropy.units as u
import matplotlib.pyplot as plt
import pandas as pd
from astropy.coordinates import SkyCoord


def visualize(img):
    plt.figure(figsize=(8, 8))
    plt.imshow(img, cmap='grey')
    plt.colorbar(label="Интенсивность (норм.)")
    plt.title("Предобработанное изображение")
    plt.xlabel("Пиксели по X")
    plt.ylabel("Пиксели по Y")
    plt.tight_layout()
    plt.show()


def visualize_detections_with_catalog_and_truth(
    image,
    detections,
    star_catalog_path,
    truth_catalog_path,
    wcs,
    title="Детекции, Звезды и истинные объекты"
):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(image, cmap='gray', origin='lower')
    ax.set_title(title)
    plt.colorbar(ax.images[0], ax=ax, label='Интенсивность')

    image_width = image.shape[1]

    # звёзды из каталога
    star_catalog = pd.read_csv(star_catalog_path)
    star_coords = SkyCoord(
        ra=star_catalog["RightAscension"].values * u.rad,
        dec=star_catalog["Declination"].values * u.rad
    )
    star_x, star_y = wcs.world_to_pixel(star_coords)
    corrected_star_x = image_width - star_x  # отразим горизонтально
    ax.scatter(corrected_star_x, star_y, color='cyan', s=15, marker='x',
               label='Звезды из каталога')

    # эталонные объекты
    truth_df = pd.read_csv(truth_catalog_path)
    truth_coords = SkyCoord(
        ra=truth_df["rightAscension"].values * u.rad,
        dec=truth_df["declination"].values * u.rad
    )
    truth_x, truth_y = wcs.world_to_pixel(truth_coords)
    corrected_truth_x = image_width - truth_x
    ax.scatter(corrected_truth_x, truth_y, color='lime', s=30, marker='*',
               label='Истинные объекты')

    # детектированные кандидаты
    scale = 10.0
    for idx, det in enumerate(detections):
        x, y = det['x'], det['y']
        vx, vy = det.get('vx', 0), det.get('vy', 0)
        label = (f"#{idx+1} | v=({vx:.1f}, {vy:.1f})\nSNR="
                 f"{det.get('snr', 0):.1f}")
        ax.plot(x, y, 'ro', markersize=5)
        ax.arrow(x, y, scale * vx, scale * vy, head_width=3, head_length=5,
                 fc='yellow', ec='yellow')
        ax.text(x + 5, y + 5, label, color='yellow', fontsize=8, ha='left',
                va='bottom')

    ax.set_xlabel("X [pixels]")
    ax.set_ylabel("Y [pixels]")
    ax.legend(loc="upper right")
    ax.set_xlim(0, image.shape[1])
    ax.set_ylim(0, image.shape[0])
    ax.grid(False)
    plt.tight_layout()
    plt.show()
