import math

import numpy as np

from watermarking.metrics import bit_error_rate, mse, normalized_correlation, psnr, ssim_score


def test_mse_and_psnr_for_identical_images():
    image = np.full((8, 8), 128, dtype=np.uint8)
    assert mse(image, image) == 0.0
    assert math.isinf(psnr(image, image))


def test_bit_error_rate_counts_different_bits():
    expected = np.array([[0, 1], [1, 0]], dtype=np.uint8)
    actual = np.array([[0, 0], [1, 1]], dtype=np.uint8)
    assert bit_error_rate(expected, actual) == 0.5


def test_normalized_correlation_identical_watermarks():
    watermark = np.array([[0, 255], [255, 0]], dtype=np.uint8)
    assert normalized_correlation(watermark, watermark) == 1.0


def test_ssim_identical_images():
    image = np.full((16, 16), 127, dtype=np.uint8)
    assert ssim_score(image, image) == 1.0
