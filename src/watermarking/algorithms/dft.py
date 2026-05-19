from __future__ import annotations

import numpy as np

from watermarking.algorithms.base import ExtractionResult, Watermarker, WatermarkResult, ensure_grayscale_float, normalize_uint8, watermark_to_bits


class DFTWatermarker(Watermarker):
    method_name = "dft"

    def __init__(self, alpha: float = 10.0, radius_ratio: float = 0.28, **params) -> None:
        super().__init__(alpha=alpha, radius_ratio=radius_ratio, **params)
        self.alpha = float(alpha)
        self.radius_ratio = float(radius_ratio)

    def _positions(self, image_shape: tuple[int, int], watermark_shape: tuple[int, int]) -> list[tuple[int, int]]:
        height, width = image_shape
        wh, ww = watermark_shape
        capacity = wh * ww
        center_y, center_x = height // 2, width // 2
        radius_y = max(wh, int(height * self.radius_ratio))
        radius_x = max(ww, int(width * self.radius_ratio))
        positions: list[tuple[int, int]] = []
        for y in range(center_y - radius_y, center_y + radius_y):
            for x in range(center_x + 3, center_x + radius_x):
                if 0 <= y < height and 0 <= x < width:
                    mirror_y = (height - y) % height
                    mirror_x = (width - x) % width
                    if (y, x) != (mirror_y, mirror_x):
                        positions.append((y, x))
                        if len(positions) == capacity:
                            return positions
        raise ValueError(f"Watermark shape {watermark_shape} exceeds DFT capacity {len(positions)} for image shape {image_shape}.")

    def embed(self, image: np.ndarray, watermark: np.ndarray) -> WatermarkResult:
        host = ensure_grayscale_float(image)
        bits = watermark_to_bits(watermark)
        signs = bits.astype(np.float64) * 2 - 1
        spectrum = np.fft.fftshift(np.fft.fft2(host))
        positions = self._positions(host.shape, bits.shape)
        flat_signs = signs.ravel()
        height, width = host.shape
        strength = self.alpha * height * width / 32.0
        for idx, (y, x) in enumerate(positions):
            spectrum[y, x] += strength * flat_signs[idx]
            spectrum[(height - y) % height, (width - x) % width] += strength * flat_signs[idx]
        watermarked = np.fft.ifft2(np.fft.ifftshift(spectrum)).real
        return WatermarkResult(
            image=normalize_uint8(watermarked),
            watermark=np.where(bits > 0, 255, 0).astype(np.uint8),
            metadata={"method": self.method_name, "alpha": self.alpha, "blind": False},
        )

    def extract(self, image: np.ndarray, watermark_shape: tuple[int, int], original_image: np.ndarray | None = None) -> ExtractionResult:
        if original_image is None:
            raise ValueError("DFT extraction requires original_image because this is a non-blind baseline.")
        watermarked = ensure_grayscale_float(image)
        original = ensure_grayscale_float(original_image)
        if watermarked.shape != original.shape:
            raise ValueError(f"Shape mismatch: {watermarked.shape} != {original.shape}.")
        difference = np.fft.fftshift(np.fft.fft2(watermarked - original))
        positions = self._positions(watermarked.shape, watermark_shape)
        bits = np.array([1 if difference[y, x].real >= 0 else 0 for y, x in positions], dtype=np.uint8)
        watermark = (bits.reshape(watermark_shape) * 255).astype(np.uint8)
        return ExtractionResult(watermark=watermark, metadata={"method": self.method_name, "blind": False})
