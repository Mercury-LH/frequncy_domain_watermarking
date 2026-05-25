from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import requests


def read_grayscale(path: str | Path) -> np.ndarray:
    image_path = Path(path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}. Put the file there or run demo data preparation.")
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Failed to read image as grayscale: {image_path}.")
    return image


def read_color(path: str | Path) -> np.ndarray:
    image_path = Path(path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}. Put the file there or run demo data preparation.")
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Failed to read image as color: {image_path}.")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def luminance_channel(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)[:, :, 0]


def replace_luminance(image: np.ndarray, luminance: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return luminance
    ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
    ycrcb[:, :, 0] = np.clip(luminance, 0, 255).astype(np.uint8)
    return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)


def save_image(path: str | Path, image: np.ndarray) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if image.ndim == 3:
        image = cv2.cvtColor(np.clip(image, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
    ok = cv2.imwrite(str(output_path), np.clip(image, 0, 255).astype(np.uint8))
    if not ok:
        raise ValueError(f"Failed to save image: {output_path}.")


def save_grayscale(path: str | Path, image: np.ndarray) -> None:
    save_image(path, image)


def prepare_watermark(watermark: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    resized = cv2.resize(watermark, (shape[1], shape[0]), interpolation=cv2.INTER_AREA)
    return np.where(resized > 127, 255, 0).astype(np.uint8)


def create_synthetic_image(size: tuple[int, int] = (512, 512)) -> np.ndarray:
    height, width = size
    y = np.linspace(0, 1, height, dtype=np.float64)[:, None]
    x = np.linspace(0, 1, width, dtype=np.float64)[None, :]
    gradient = 120 + 80 * x + 40 * y
    texture = 25 * np.sin(12 * np.pi * x) * np.cos(8 * np.pi * y)
    image = gradient + texture
    cv2.circle(image, (width // 3, height // 3), min(height, width) // 8, 70, -1)
    cv2.rectangle(image, (width // 2, height // 2), (width * 3 // 4, height * 3 // 4), 210, -1)
    return np.clip(image, 0, 255).astype(np.uint8)


def create_synthetic_watermark(size: tuple[int, int] = (64, 64)) -> np.ndarray:
    image = np.zeros(size, dtype=np.uint8)
    cv2.putText(image, "BUAA", (3, size[0] // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.55, 255, 1, cv2.LINE_AA)
    cv2.rectangle(image, (4, 4), (size[1] - 5, size[0] - 5), 255, 1)
    return np.where(image > 127, 255, 0).astype(np.uint8)


def _download(url: str, path: Path) -> bool:
    try:
        response = requests.get(url, timeout=12)
        response.raise_for_status()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(response.content)
        return cv2.imread(str(path), cv2.IMREAD_GRAYSCALE) is not None
    except requests.RequestException:
        return False


def ensure_demo_data(image_path: str | Path, watermark_path: str | Path, allow_download: bool = True) -> None:
    image_file = Path(image_path)
    watermark_file = Path(watermark_path)
    if image_file.exists() and watermark_file.exists():
        return

    image_file.parent.mkdir(parents=True, exist_ok=True)
    watermark_file.parent.mkdir(parents=True, exist_ok=True)

    downloaded = False
    if allow_download and not image_file.exists():
        downloaded = _download("https://sipi.usc.edu/database/download.php?vol=misc&img=4.2.04", image_file)

    if not image_file.exists() or not downloaded:
        save_grayscale(image_file, create_synthetic_image())

    if not watermark_file.exists():
        save_grayscale(watermark_file, create_synthetic_watermark())
