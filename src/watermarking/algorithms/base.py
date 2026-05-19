from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class WatermarkResult:
    image: np.ndarray
    watermark: np.ndarray
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ExtractionResult:
    watermark: np.ndarray
    metadata: dict[str, Any]


class Watermarker(ABC):
    method_name: str

    def __init__(self, **params: Any) -> None:
        self.params = params

    @abstractmethod
    def embed(self, image: np.ndarray, watermark: np.ndarray) -> WatermarkResult:
        raise NotImplementedError

    @abstractmethod
    def extract(
        self,
        image: np.ndarray,
        watermark_shape: tuple[int, int],
        original_image: np.ndarray | None = None,
    ) -> ExtractionResult:
        raise NotImplementedError


def ensure_grayscale_float(image: np.ndarray) -> np.ndarray:
    if image.ndim != 2:
        raise ValueError(f"Expected a grayscale image with 2 dimensions, got shape {image.shape}.")
    return image.astype(np.float64, copy=False)


def normalize_uint8(image: np.ndarray) -> np.ndarray:
    return np.clip(np.rint(image), 0, 255).astype(np.uint8)


def watermark_to_bits(watermark: np.ndarray) -> np.ndarray:
    if watermark.ndim != 2:
        raise ValueError(f"Expected a 2D watermark, got shape {watermark.shape}.")
    return (watermark > 127).astype(np.uint8)
