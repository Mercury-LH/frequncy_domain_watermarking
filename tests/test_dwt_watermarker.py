import numpy as np

from watermarking.algorithms.dwt import DWTWatermarker
from watermarking.metrics import bit_error_rate, psnr


def test_dwt_blind_embed_extract_recovers_watermark():
    rng = np.random.default_rng(17)
    image = rng.integers(20, 230, size=(128, 128), dtype=np.uint8)
    watermark = rng.choice([0, 255], size=(16, 16)).astype(np.uint8)
    watermarker = DWTWatermarker(alpha=8.0, wavelet="haar", subband="hl")

    embedded = watermarker.embed(image, watermark)
    extracted = watermarker.extract(embedded.image, watermark.shape)

    assert embedded.image.shape == image.shape
    assert embedded.metadata["blind"] is True
    assert psnr(image, embedded.image) > 18
    assert bit_error_rate(watermark, extracted.watermark) < 0.2
