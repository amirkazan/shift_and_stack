import numpy as np


def form_detection_results(candidates: dict, series_time: float,
                           zero_point_mag: float = 20.0) -> list[dict]:

    results = []
    for c in candidates:
        ra = c.get('ra', None)
        dec = c.get('dec', None)
        vx = c['vx']
        vy = c['vy']
        signal = c['signal']

        # оценка угловой скорости и направления
        omega = np.sqrt(vx**2 + vy**2)
        phi = np.arctan2(vy, vx)

        magnitude = zero_point_mag - 2.5 * np.log10(signal + 1e-8)
        results.append({
            'ra': ra,
            'dec': dec,
            'time': series_time,
            'omega': omega,
            'phi': phi,
            'mag': magnitude,
            'snr': c['snr'],
        })
    return results
