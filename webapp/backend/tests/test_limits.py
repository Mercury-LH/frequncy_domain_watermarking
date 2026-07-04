from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

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
