from pathlib import Path

import numpy as np
import pandas as pd

from watermarking.visualization import save_comparison_figure, save_metric_curve, save_spectrum_figure


def test_visualization_writes_expected_files(tmp_path):
    image = np.full((32, 32), 128, dtype=np.uint8)
    watermark = np.zeros((8, 8), dtype=np.uint8)
    comparison = tmp_path / "comparison.png"
    spectrum = tmp_path / "spectrum.png"
    curve = tmp_path / "curve.png"
    save_comparison_figure(comparison, image, image, watermark, watermark, title="demo")
    save_spectrum_figure(spectrum, image)
    save_metric_curve(curve, pd.DataFrame({"strength": [1, 2], "psnr": [30, 25], "method": ["dft", "dft"]}), x="strength", y="psnr", hue="method", title="curve")
    assert comparison.exists()
    assert spectrum.exists()
    assert curve.exists()
