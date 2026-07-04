from __future__ import annotations

import io

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from webapp.backend.app import create_app


@pytest.fixture()
def unrset_client() -> TestClient:
    """Client without limiter reset — lets rate-limit counts accumulate."""
    return TestClient(create_app())


def test_rate_limit_returns_bilingual_429(unrset_client, synthetic_image):
    from webapp.backend.tests.conftest import encode_png

    payload = {"files": {"image": ("x.png", encode_png(synthetic_image), "image/png")}}
    last = None
    for _ in range(25):
        last = unrset_client.post("/api/extract", **payload)
        if last.status_code == 429:
            break
    assert last is not None and last.status_code == 429
    assert last.json()["error"]["code"] == "rate_limited"


def _make_large_png(width: int = 7000, height: int = 7000) -> bytes:
    """Generate a large-pixel PNG that compresses to a small file (zeros)."""
    buf = io.BytesIO()
    Image.fromarray(np.zeros((height, width), dtype=np.uint8)).save(buf, format="PNG")
    return buf.getvalue()


def test_pixel_bomb_returns_image_too_large(client):
    large_png = _make_large_png()
    response = client.post(
        "/api/embed",
        data={"method": "dct", "strength": "12.0", "watermark_text": "test"},
        files={"image": ("bomb.png", large_png, "image/png")},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "image_too_large"


def test_decompression_bomb_above_pillow_threshold_rejected(client):
    """A PNG above Pillow's ~178MP DecompressionBombError threshold must still be
    rejected: PIL raises DecompressionBombError before our 40MP size check runs,
    and that must map to image_too_large rather than falling through to cv2."""
    buf = io.BytesIO()
    Image.new("L", (13780, 13780)).save(buf, format="PNG")  # ~189MP, tiny payload
    response = client.post(
        "/api/embed",
        data={"method": "dct", "strength": "12.0", "watermark_text": "test"},
        files={"image": ("megabomb.png", buf.getvalue(), "image/png")},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "image_too_large"
