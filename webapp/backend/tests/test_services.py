from __future__ import annotations

import numpy as np
import pytest

from webapp.backend import services
from webapp.backend.errors import ApiError
from webapp.backend.tests.conftest import encode_png


def test_decode_host_image_returns_rgb(synthetic_image):
    data = encode_png(synthetic_image)
    decoded = services.decode_host_image(data)
    assert decoded.ndim == 3 and decoded.shape[2] == 3
    assert decoded.dtype == np.uint8


def test_decode_host_image_downscales_long_side():
    big = np.random.default_rng(0).integers(0, 255, (300, 2048), dtype=np.uint8)
    decoded = services.decode_host_image(encode_png(big))
    assert max(decoded.shape[:2]) == 1024


def test_decode_host_image_rejects_garbage():
    with pytest.raises(ApiError) as excinfo:
        services.decode_host_image(b"not an image at all")
    assert excinfo.value.code == "unsupported_format"


def test_decode_host_image_rejects_oversize():
    with pytest.raises(ApiError) as excinfo:
        services.decode_host_image(b"\x00" * (services.MAX_BYTES + 1))
    assert excinfo.value.code == "file_too_large"


def test_decode_host_image_rejects_tiny():
    tiny = np.zeros((64, 64), dtype=np.uint8)
    with pytest.raises(ApiError) as excinfo:
        services.decode_host_image(encode_png(tiny))
    assert excinfo.value.code == "image_too_small"


def test_decode_watermark_image_is_grayscale(synthetic_watermark):
    decoded = services.decode_watermark_image(encode_png(synthetic_watermark))
    assert decoded.ndim == 2
