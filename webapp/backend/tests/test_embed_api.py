from __future__ import annotations

import base64

from webapp.backend.tests.conftest import encode_png


def _embed(client, synthetic_image, synthetic_watermark, **overrides):
    data = {"method": "dct", "strength": "12.0"}
    data.update({k: v for k, v in overrides.items() if not k.endswith("_file")})
    files = {"image": ("host.png", encode_png(synthetic_image), "image/png")}
    if "watermark_file" in overrides:
        files["watermark_file"] = ("wm.png", overrides["watermark_file"], "image/png")
    return client.post("/api/embed", data=data, files=files)


def test_embed_with_watermark_file(client, synthetic_image, synthetic_watermark):
    response = _embed(client, synthetic_image, synthetic_watermark, watermark_file=encode_png(synthetic_watermark))
    assert response.status_code == 200
    body = response.json()
    assert body["metrics"]["psnr"] > 30
    assert body["params"]["method"] == "dct"
    assert base64.b64decode(body["watermarked_png_b64"])[:8] == b"\x89PNG\r\n\x1a\n"


def test_embed_with_text_watermark(client, synthetic_image, synthetic_watermark):
    response = _embed(client, synthetic_image, synthetic_watermark, watermark_text="水印")
    assert response.status_code == 200


def test_embed_without_watermark_400(client, synthetic_image, synthetic_watermark):
    response = _embed(client, synthetic_image, synthetic_watermark)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "missing_watermark"


def test_embed_bad_method_400(client, synthetic_image, synthetic_watermark):
    response = _embed(client, synthetic_image, synthetic_watermark, watermark_text="hi", method="rsa")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_method"
