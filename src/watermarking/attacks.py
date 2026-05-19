from __future__ import annotations

import cv2
import numpy as np


def jpeg_compress(image: np.ndarray, quality: int) -> np.ndarray:
    if not 1 <= quality <= 100:
        raise ValueError(f"JPEG quality must be in [1, 100], got {quality}.")
    ok, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, int(quality)])
    if not ok:
        raise ValueError("Failed to encode image as JPEG.")
    decoded = cv2.imdecode(encoded, cv2.IMREAD_GRAYSCALE)
    if decoded is None:
        raise ValueError("Failed to decode JPEG image.")
    return decoded.astype(np.uint8)


def resize_attack(image: np.ndarray, scale: float) -> np.ndarray:
    if scale <= 0:
        raise ValueError(f"Scale must be positive, got {scale}.")
    height, width = image.shape
    small = cv2.resize(image, (max(1, int(width * scale)), max(1, int(height * scale))), interpolation=cv2.INTER_LINEAR)
    restored = cv2.resize(small, (width, height), interpolation=cv2.INTER_LINEAR)
    return restored.astype(np.uint8)


def gaussian_noise(image: np.ndarray, sigma: float, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, sigma, size=image.shape)
    return np.clip(image.astype(np.float64) + noise, 0, 255).astype(np.uint8)


def blur_attack(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    if kernel_size % 2 == 0 or kernel_size < 1:
        raise ValueError("Kernel size must be a positive odd integer.")
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0).astype(np.uint8)


def crop_attack(image: np.ndarray, ratio: float = 0.1) -> np.ndarray:
    if not 0 <= ratio < 0.5:
        raise ValueError(f"Crop ratio must be in [0, 0.5), got {ratio}.")
    height, width = image.shape
    dy = int(height * ratio)
    dx = int(width * ratio)
    cropped = image[dy : height - dy, dx : width - dx]
    return cv2.resize(cropped, (width, height), interpolation=cv2.INTER_LINEAR).astype(np.uint8)


def apply_attack(image: np.ndarray, attack: str, **params) -> np.ndarray:
    key = attack.lower()
    if key == "jpeg":
        return jpeg_compress(image, quality=int(params.get("quality", 70)))
    if key == "resize":
        return resize_attack(image, scale=float(params.get("scale", 0.5)))
    if key == "noise":
        return gaussian_noise(image, sigma=float(params.get("sigma", 10)), seed=int(params.get("seed", 42)))
    if key == "blur":
        return blur_attack(image, kernel_size=int(params.get("kernel_size", 3)))
    if key == "crop":
        return crop_attack(image, ratio=float(params.get("ratio", 0.1)))
    raise ValueError(f"Unknown attack '{attack}'.")
