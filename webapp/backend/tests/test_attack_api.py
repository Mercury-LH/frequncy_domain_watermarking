from __future__ import annotations

import base64

from webapp.backend.tests.conftest import encode_png
from webapp.backend.tests.test_extract_api import _embedded_png


def test_attack_jpeg_reports_watermark_quality(client, synthetic_image, synthetic_watermark):
    watermarked = _embedded_png(client, synthetic_image, synthetic_watermark)
    response = client.post(
        "/api/attack",
        data={"attack": "jpeg", "param": "90"},
        files={"image": ("wm.png", watermarked, "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert 0.0 <= body["watermark"]["ber"] <= 1.0
    assert base64.b64decode(body["attacked_png_b64"])


def test_attack_bad_type_400(client, synthetic_image, synthetic_watermark):
    watermarked = _embedded_png(client, synthetic_image, synthetic_watermark)
    response = client.post(
        "/api/attack",
        data={"attack": "steal", "param": "1"},
        files={"image": ("wm.png", watermarked, "image/png")},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_attack"
