import numpy as np
import pytest

from watermarking.algorithms.dft import DFTWatermarker
from watermarking.metrics import bit_error_rate, psnr


def test_dft_embed_extract_recovers_watermark_with_original():
    rng = np.random.default_rng(7)
    image = rng.integers(30, 220, size=(128, 128), dtype=np.uint8)
    watermark = rng.choice([0, 255], size=(16, 16)).astype(np.uint8)
    watermarker = DFTWatermarker(alpha=30.0, radius_ratio=0.25)

    embedded = watermarker.embed(image, watermark)
    extracted = watermarker.extract(embedded.image, watermark.shape, original_image=image)

    assert embedded.image.shape == image.shape
    assert psnr(image, embedded.image) > 20
    assert bit_error_rate(watermark, extracted.watermark) < 0.05


def test_dft_extract_requires_original_image():
    image = np.full((64, 64), 128, dtype=np.uint8)
    watermarker = DFTWatermarker(alpha=10.0)
    with pytest.raises(ValueError, match="requires original_image"):
        watermarker.extract(image, (8, 8))
