from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
for p in (str(REPO_ROOT), str(REPO_ROOT / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

import warnings

warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL.*")

import numpy as np
import pytest
from fastapi.testclient import TestClient

from watermarking.io_utils import create_synthetic_image, create_synthetic_watermark
from webapp.backend.app import create_app


@pytest.fixture()
def client() -> TestClient:
    from webapp.backend.routes import limiter

    limiter.reset()
    return TestClient(create_app())


@pytest.fixture()
def synthetic_image() -> np.ndarray:
    return create_synthetic_image((512, 512))


@pytest.fixture()
def synthetic_watermark() -> np.ndarray:
    return create_synthetic_watermark((64, 64))


def encode_png(array: np.ndarray) -> bytes:
    import cv2

    ok, buf = cv2.imencode(".png", array)
    assert ok
    return buf.tobytes()
