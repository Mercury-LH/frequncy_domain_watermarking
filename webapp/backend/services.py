from __future__ import annotations

import cv2
import numpy as np

from webapp.backend import errors

MAX_BYTES = 10 * 1024 * 1024
MAX_SIDE = 1024
MIN_SIDE = 128


def downscale(image: np.ndarray, max_side: int = MAX_SIDE) -> np.ndarray:
    height, width = image.shape[:2]
    longest = max(height, width)
    if longest <= max_side:
        return image
    scale = max_side / longest
    return cv2.resize(image, (max(1, round(width * scale)), max(1, round(height * scale))), interpolation=cv2.INTER_AREA)


def _decode(data: bytes, flags: int) -> np.ndarray:
    if len(data) > MAX_BYTES:
        raise errors.file_too_large()
    array = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), flags)
    if array is None:
        raise errors.unsupported_format()
    return array


def decode_host_image(data: bytes) -> np.ndarray:
    bgr = _decode(data, cv2.IMREAD_COLOR)
    if min(bgr.shape[:2]) < MIN_SIDE:
        raise errors.image_too_small()
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return downscale(rgb)


def decode_watermark_image(data: bytes) -> np.ndarray:
    gray = _decode(data, cv2.IMREAD_GRAYSCALE)
    return downscale(gray, 512)
