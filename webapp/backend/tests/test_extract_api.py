from __future__ import annotations

import base64

from webapp.backend.tests.conftest import encode_png


def _embedded_png(client, synthetic_image, synthetic_watermark, method="dct", strength="12.0"):
    response = client.post(
        "/api/embed",
        data={"method": method, "strength": strength},
        files={
            "image": ("host.png", encode_png(synthetic_image), "image/png"),
            "watermark_file": ("wm.png", encode_png(synthetic_watermark), "image/png"),
        },
    )
    assert response.status_code == 200
    return base64.b64decode(response.json()["watermarked_png_b64"])


def test_extract_autoreads_png_params(client, synthetic_image, synthetic_watermark):
    watermarked = _embedded_png(client, synthetic_image, synthetic_watermark)
    response = client.post(
        "/api/extract",
        files={
            "image": ("wm.png", watermarked, "image/png"),
            "reference_watermark": ("ref.png", encode_png(synthetic_watermark), "image/png"),
        },
    )
    assert response.status_code == 200
    assert response.json()["nc"] > 0.85


def test_extract_dft_missing_original_422(client, synthetic_image, synthetic_watermark):
    watermarked = _embedded_png(client, synthetic_image, synthetic_watermark, method="dft", strength="10.0")
    response = client.post("/api/extract", files={"image": ("wm.png", watermarked, "image/png")})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "dft_requires_original"


def test_extract_bad_dims_returns_bilingual_400(client, synthetic_image):
    from webapp.backend.tests.conftest import encode_png
    r = client.post("/api/extract", data={"method": "dct", "wm_w": "100000", "wm_h": "100000"},
                    files={"image": ("x.png", encode_png(synthetic_image), "image/png")})
    assert r.status_code == 400
    body = r.json()["error"]
    assert body["code"] == "bad_params" and body["zh"] and body["en"]


def test_extract_without_params_or_meta_400(client, synthetic_image):
    response = client.post("/api/extract", files={"image": ("x.png", encode_png(synthetic_image), "image/png")})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "missing_params"
