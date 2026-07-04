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


def test_render_text_watermark_chinese_not_blank():
    bitmap = services.render_text_watermark("水印测试")
    assert bitmap.shape == (256, 256)
    assert set(np.unique(bitmap)).issubset({0, 255})
    assert (bitmap == 255).mean() > 0.01


def test_render_text_watermark_differs_by_text():
    a = services.render_text_watermark("ABC")
    b = services.render_text_watermark("XYZ")
    assert (a != b).any()


def test_render_text_watermark_rejects_long_text():
    with pytest.raises(ApiError) as excinfo:
        services.render_text_watermark("字" * 21)
    assert excinfo.value.code == "text_too_long"


def test_render_text_watermark_rejects_empty():
    with pytest.raises(ApiError) as excinfo:
        services.render_text_watermark("   ")
    assert excinfo.value.code == "missing_watermark"


def test_render_text_watermark_rejects_tiny_canvas():
    with pytest.raises(ValueError):
        services.render_text_watermark("hi", canvas=8)


def test_spectrum_png_b64_decodes(synthetic_image):
    import base64

    b64 = services.spectrum_png_b64(synthetic_image.astype(np.float64))
    raw = base64.b64decode(b64)
    assert raw[:8] == b"\x89PNG\r\n\x1a\n"


def test_png_params_roundtrip(synthetic_image):
    import cv2

    rgb = cv2.cvtColor(synthetic_image, cv2.COLOR_GRAY2RGB)
    params = {"v": 1, "method": "dct", "strength": 12.0, "wm_w": 64, "wm_h": 64}
    data = services.png_bytes_with_params(rgb, params)
    assert services.read_png_params(data) == params


def test_read_png_params_none_when_absent(synthetic_image):
    assert services.read_png_params(encode_png(synthetic_image)) is None


def test_choose_watermark_side_512():
    assert services.choose_watermark_side(512, 512) == 64


def test_choose_watermark_side_small_image():
    assert services.choose_watermark_side(256, 256) == 32


def test_strength_validation():
    with pytest.raises(ApiError) as excinfo:
        services.validate_strength("dct", 100.0)
    assert excinfo.value.code == "bad_strength"


@pytest.mark.parametrize("method", ["dct", "dft"])
def test_embed_extract_roundtrip(method, synthetic_image, synthetic_watermark):
    import cv2

    rgb = cv2.cvtColor(synthetic_image, cv2.COLOR_GRAY2RGB)
    result = services.run_embed(rgb, synthetic_watermark, method, services.STRENGTH_RANGES[method][2])
    assert result["metrics"]["psnr"] > 30.0
    params = result["params"]
    watermarked = services.decode_host_image(__import__("base64").b64decode(result["watermarked_png_b64"]))
    original = rgb if method == "dft" else None
    extraction = services.run_extract(
        watermarked, method, params["wm_w"], params["wm_h"],
        original_rgb=original, reference_watermark=synthetic_watermark,
    )
    assert extraction["nc"] > 0.85


def test_run_extract_dft_without_original_raises(synthetic_image):
    import cv2

    rgb = cv2.cvtColor(synthetic_image, cv2.COLOR_GRAY2RGB)
    with pytest.raises(ApiError) as excinfo:
        services.run_extract(rgb, "dft", 64, 64)
    assert excinfo.value.code == "dft_requires_original"


def test_attack_image_jpeg_keeps_shape(synthetic_image):
    import cv2

    rgb = cv2.cvtColor(synthetic_image, cv2.COLOR_GRAY2RGB)
    attacked = services.attack_image(rgb, "jpeg", 60)
    assert attacked.shape == rgb.shape


def test_run_attack_dct_survives_mild_jpeg(synthetic_image, synthetic_watermark):
    import base64

    import cv2

    rgb = cv2.cvtColor(synthetic_image, cv2.COLOR_GRAY2RGB)
    embed = services.run_embed(rgb, synthetic_watermark, "dct", 12.0)
    watermarked = services.decode_host_image(base64.b64decode(embed["watermarked_png_b64"]))
    outcome = services.run_attack(watermarked, "jpeg", 90, "dct", 64, 64)
    assert outcome["watermark"]["nc"] > 0.5


def test_embed_extract_roundtrip_dwt_structural(synthetic_image, synthetic_watermark):
    """DWT blind extraction (median threshold in src/watermarking) cannot recover
    sparse watermarks without the original image: measured NC ~= 0.05 across the
    full strength range. The webapp ships DWT as an embedding demo, so this test
    locks the pipeline contract (quality, shapes, metric presence), not fidelity."""
    import base64

    import cv2

    rgb = cv2.cvtColor(synthetic_image, cv2.COLOR_GRAY2RGB)
    result = services.run_embed(rgb, synthetic_watermark, "dwt", services.STRENGTH_RANGES["dwt"][2])
    assert result["metrics"]["psnr"] > 30.0
    params = result["params"]
    watermarked = services.decode_host_image(base64.b64decode(result["watermarked_png_b64"]))
    extraction = services.run_extract(
        watermarked, "dwt", params["wm_w"], params["wm_h"], reference_watermark=synthetic_watermark
    )
    wm = services._decode(base64.b64decode(extraction["watermark_png_b64"]), cv2.IMREAD_GRAYSCALE)
    assert wm.shape == (params["wm_h"], params["wm_w"])
    assert "nc" in extraction and "ber" in extraction
