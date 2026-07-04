from __future__ import annotations

import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

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


_FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "C:/Windows/Fonts/msyh.ttc",
]


def find_cjk_font() -> str:
    override = os.environ.get("WATERMARK_FONT")
    candidates = [override] + _FONT_CANDIDATES if override else _FONT_CANDIDATES
    for path in candidates:
        if path and os.path.exists(path):
            return path
    raise RuntimeError("No CJK-capable font found; set WATERMARK_FONT to a .ttf/.ttc path.")


def render_text_watermark(text: str, canvas: int = 256) -> np.ndarray:
    cleaned = text.strip()
    if not cleaned:
        raise errors.missing_watermark()
    if len(cleaned) > 20:
        raise errors.text_too_long()
    if canvas <= 8:
        raise ValueError("canvas must be larger than 8 pixels")
    font_path = find_cjk_font()
    image = Image.new("L", (canvas, canvas), 0)
    draw = ImageDraw.Draw(image)
    size = canvas
    while size > 8:
        font = ImageFont.truetype(font_path, size)
        left, top, right, bottom = draw.textbbox((0, 0), cleaned, font=font)
        if right - left <= canvas - 16 and bottom - top <= canvas - 16:
            break
        size = int(size * 0.85)
    x = (canvas - (right - left)) // 2 - left
    y = (canvas - (bottom - top)) // 2 - top
    draw.text((x, y), cleaned, fill=255, font=font)
    array = np.array(image, dtype=np.uint8)
    return np.where(array > 127, 255, 0).astype(np.uint8)
