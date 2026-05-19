import numpy as np

from watermarking.algorithms.dct import DCTWatermarker
from watermarking.metrics import bit_error_rate, psnr


def test_dct_blind_embed_extract_recovers_watermark_without_original():
    rng = np.random.default_rng(11)
    image = rng.integers(20, 230, size=(128, 128), dtype=np.uint8)
    watermark = rng.choice([0, 255], size=(8, 8)).astype(np.uint8)
    watermarker = DCTWatermarker(delta=28.0, block_size=8)

    embedded = watermarker.embed(image, watermark)
    extracted = watermarker.extract(embedded.image, watermark.shape)

    assert embedded.image.shape == image.shape
    assert embedded.metadata["blind"] is True
    assert psnr(image, embedded.image) > 20
    assert bit_error_rate(watermark, extracted.watermark) < 0.1
