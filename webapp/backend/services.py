from __future__ import annotations

import base64
import io
import json
import math
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo

from webapp.backend import errors
from watermarking.io_utils import luminance_channel, prepare_watermark, replace_luminance
from watermarking.metrics import image_quality, watermark_quality
from watermarking.registry import create_watermarker

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
    try:
        with Image.open(io.BytesIO(data)) as probe:
            width, height = probe.size
        if width * height > 40_000_000:
            raise errors.image_too_large()
    except errors.ApiError:
        raise
    except Exception:
        pass  # not PIL-readable; let cv2.imdecode be the authority
    array = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), flags)
    if array is None:
        raise errors.unsupported_format()
    return array


def decode_host_image(data: bytes) -> np.ndarray:
    bgr = _decode(data, cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    rgb = downscale(rgb)
    if min(rgb.shape[:2]) < MIN_SIDE:
        raise errors.image_too_small()
    return rgb


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


PARAMS_KEYWORD = "watermark-params"


def png_b64(image: np.ndarray) -> str:
    if image.ndim == 3:
        encoded = cv2.imencode(".png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))[1]
    else:
        encoded = cv2.imencode(".png", image)[1]
    return base64.b64encode(encoded.tobytes()).decode("ascii")


def spectrum_png_b64(gray: np.ndarray) -> str:
    spectrum = np.fft.fftshift(np.fft.fft2(gray.astype(np.float64)))
    magnitude = np.log1p(np.abs(spectrum))
    lo, hi = float(magnitude.min()), float(magnitude.max())
    normalized = np.zeros_like(magnitude) if hi <= lo else (magnitude - lo) / (hi - lo)
    return png_b64((normalized * 255).astype(np.uint8))


def png_bytes_with_params(image_rgb: np.ndarray, params: dict) -> bytes:
    info = PngInfo()
    info.add_text(PARAMS_KEYWORD, json.dumps(params))
    buffer = io.BytesIO()
    Image.fromarray(image_rgb).save(buffer, format="PNG", pnginfo=info)
    return buffer.getvalue()


def read_png_params(data: bytes) -> dict | None:
    try:
        text = Image.open(io.BytesIO(data)).text.get(PARAMS_KEYWORD)
    except Exception:
        return None
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


STRENGTH_RANGES: dict[str, tuple[float, float, float]] = {
    "dct": (4.0, 24.0, 12.0),
    "dft": (2.0, 20.0, 3.0),   # default lowered from 10.0 → 3.0 so PSNR > 30 dB
    "dwt": (0.01, 0.5, 0.05),  # research default; extraction fidelity unreachable at any alpha (DWT ships as embedding demo)
}
_STRENGTH_PARAM = {"dct": "delta", "dft": "alpha", "dwt": "alpha"}


def validate_method(method: str) -> str:
    key = method.lower()
    if key not in STRENGTH_RANGES:
        raise errors.bad_method()
    return key


def validate_strength(method: str, strength: float) -> float:
    low, high, _ = STRENGTH_RANGES[validate_method(method)]
    if not low <= strength <= high:
        raise errors.bad_strength(method, low, high)
    return float(strength)


def choose_watermark_side(height: int, width: int) -> int:
    side = min(64, int(math.sqrt((height // 8) * (width // 8))))
    if side < 8:
        raise errors.image_too_small()
    return side


def _make(method: str, strength: float):
    return create_watermarker(method, **{_STRENGTH_PARAM[method]: strength})


def _capped_quality(reference: np.ndarray, candidate: np.ndarray) -> dict:
    quality = image_quality(reference, candidate)
    return {"psnr": round(min(quality["psnr"], 99.0), 2), "ssim": round(quality["ssim"], 4)}


def run_embed(host_rgb: np.ndarray, watermark_gray: np.ndarray, method: str, strength: float) -> dict:
    method = validate_method(method)
    strength = validate_strength(method, strength)
    height, width = host_rgb.shape[:2]
    side = choose_watermark_side(height, width)
    prepared = prepare_watermark(watermark_gray, (side, side))
    luminance = luminance_channel(host_rgb)
    result = _make(method, strength).embed(luminance, prepared)
    output_rgb = replace_luminance(host_rgb, result.image)
    params = {"v": 1, "method": method, "strength": strength, "wm_w": side, "wm_h": side}
    return {
        "watermarked_png_b64": base64.b64encode(png_bytes_with_params(output_rgb, params)).decode("ascii"),
        "metrics": _capped_quality(host_rgb, output_rgb),
        "spectrum_before_b64": spectrum_png_b64(luminance),
        "spectrum_after_b64": spectrum_png_b64(result.image),
        "params": params,
        "prepared_watermark_png_b64": png_b64(prepared),
    }


def run_extract(
    image_rgb: np.ndarray,
    method: str,
    wm_w: int,
    wm_h: int,
    original_rgb: np.ndarray | None = None,
    reference_watermark: np.ndarray | None = None,
) -> dict:
    method = validate_method(method)
    if not (8 <= int(wm_w) <= 128 and 8 <= int(wm_h) <= 128):
        raise errors.bad_params()
    if method == "dft" and original_rgb is None:
        raise errors.dft_requires_original()
    luminance = luminance_channel(image_rgb)
    original = luminance_channel(original_rgb) if original_rgb is not None else None
    if original is not None and original.shape != luminance.shape:
        raise errors.shape_mismatch()
    low, high, default = STRENGTH_RANGES[method]
    extraction = _make(method, default).extract(luminance, (int(wm_h), int(wm_w)), original_image=original)
    payload: dict = {"watermark_png_b64": png_b64(extraction.watermark)}
    if reference_watermark is not None:
        reference = prepare_watermark(reference_watermark, (int(wm_h), int(wm_w)))
        quality = watermark_quality(reference, extraction.watermark)
        payload["nc"] = round(quality["nc"], 4)
        payload["ber"] = round(quality["ber"], 4)
    return payload


_ATTACKS = {"jpeg", "resize", "noise"}


def attack_image(image_rgb: np.ndarray, attack: str, param: float) -> np.ndarray:
    key = attack.lower()
    if key not in _ATTACKS:
        raise errors.bad_attack()
    if key == "jpeg":
        quality = int(np.clip(param, 1, 100))
        bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        ok, encoded = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if not ok:
            raise errors.unsupported_format()
        return cv2.cvtColor(cv2.imdecode(encoded, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    if key == "resize":
        scale = float(np.clip(param, 0.1, 1.0))
        height, width = image_rgb.shape[:2]
        small = cv2.resize(image_rgb, (max(1, int(width * scale)), max(1, int(height * scale))), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(small, (width, height), interpolation=cv2.INTER_LINEAR)
    sigma = float(np.clip(param, 0.0, 50.0))
    noise = np.random.default_rng(42).normal(0, sigma, size=image_rgb.shape)
    return np.clip(image_rgb.astype(np.float64) + noise, 0, 255).astype(np.uint8)


def run_attack(
    image_rgb: np.ndarray,
    attack: str,
    param: float,
    method: str,
    wm_w: int,
    wm_h: int,
    original_rgb: np.ndarray | None = None,
) -> dict:
    method = validate_method(method)
    if not (8 <= int(wm_w) <= 128 and 8 <= int(wm_h) <= 128):
        raise errors.bad_params()
    before = run_extract(image_rgb, method, wm_w, wm_h, original_rgb=original_rgb)
    attacked = attack_image(image_rgb, attack, param)
    after = run_extract(attacked, method, wm_w, wm_h, original_rgb=original_rgb)
    before_wm = _decode(base64.b64decode(before["watermark_png_b64"]), cv2.IMREAD_GRAYSCALE)
    after_wm = _decode(base64.b64decode(after["watermark_png_b64"]), cv2.IMREAD_GRAYSCALE)
    quality = watermark_quality(before_wm, after_wm)
    return {
        "attacked_png_b64": png_b64(attacked),
        "extracted_png_b64": after["watermark_png_b64"],
        "metrics": _capped_quality(image_rgb, attacked),
        "watermark": {"nc": round(quality["nc"], 4), "ber": round(quality["ber"], 4)},
    }
