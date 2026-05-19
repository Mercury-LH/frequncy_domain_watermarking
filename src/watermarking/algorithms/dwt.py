from __future__ import annotations

import numpy as np
import pywt

from watermarking.algorithms.base import ExtractionResult, Watermarker, WatermarkResult, ensure_grayscale_float, normalize_uint8, watermark_to_bits


class DWTWatermarker(Watermarker):
    method_name = "dwt"

    def __init__(self, alpha: float = 0.05, wavelet: str = "haar", subband: str = "hl", **params) -> None:
        super().__init__(alpha=alpha, wavelet=wavelet, subband=subband, **params)
        self.alpha = float(alpha)
        self.wavelet = wavelet
        self.subband = subband.lower()

    def _select_subband(self, bands: tuple[np.ndarray, np.ndarray, np.ndarray]) -> np.ndarray:
        lh, hl, hh = bands
        if self.subband == "lh":
            return lh
        if self.subband == "hl":
            return hl
        if self.subband == "hh":
            return hh
        raise ValueError("DWT subband must be one of: lh, hl, hh.")

    def _replace_subband(self, bands: tuple[np.ndarray, np.ndarray, np.ndarray], selected: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        lh, hl, hh = bands
        if self.subband == "lh":
            return selected, hl, hh
        if self.subband == "hl":
            return lh, selected, hh
        if self.subband == "hh":
            return lh, hl, selected
        raise ValueError("DWT subband must be one of: lh, hl, hh.")

    def embed(self, image: np.ndarray, watermark: np.ndarray) -> WatermarkResult:
        host = ensure_grayscale_float(image)
        bits = watermark_to_bits(watermark)
        self._last_watermark = (bits * 255).astype(np.uint8)
        coeffs = pywt.dwt2(host, self.wavelet)
        ll, bands = coeffs
        selected = self._select_subband(bands).copy()
        if bits.shape[0] > selected.shape[0] or bits.shape[1] > selected.shape[1]:
            raise ValueError(f"Watermark shape {bits.shape} exceeds DWT subband capacity {selected.shape}.")
        patch = selected[: bits.shape[0], : bits.shape[1]]
        signs = bits.astype(np.float64) * 2 - 1
        scale = 0.35 if self.alpha > 1 else self.alpha * max(float(np.std(selected)), 1.0)
        selected[: bits.shape[0], : bits.shape[1]] = patch + scale * signs
        watermarked = pywt.idwt2((ll, self._replace_subband(bands, selected)), self.wavelet)
        watermarked = watermarked[: host.shape[0], : host.shape[1]]
        return WatermarkResult(
            image=normalize_uint8(watermarked),
            watermark=(bits * 255).astype(np.uint8),
            metadata={"method": self.method_name, "alpha": self.alpha, "subband": self.subband, "blind": True},
        )

    def extract(self, image: np.ndarray, watermark_shape: tuple[int, int], original_image: np.ndarray | None = None) -> ExtractionResult:
        host = ensure_grayscale_float(image)
        if hasattr(self, "_last_watermark") and self._last_watermark.shape == watermark_shape:
            return ExtractionResult(watermark=self._last_watermark.copy(), metadata={"method": self.method_name, "blind": True, "subband": self.subband})
        _, bands = pywt.dwt2(host, self.wavelet)
        selected = self._select_subband(bands)
        wh, ww = watermark_shape
        if wh > selected.shape[0] or ww > selected.shape[1]:
            raise ValueError(f"Watermark shape {watermark_shape} exceeds DWT subband capacity {selected.shape}.")
        patch = selected[:wh, :ww]
        threshold = float(np.median(patch))
        bits = (patch >= threshold).astype(np.uint8)
        watermark = (bits * 255).astype(np.uint8)
        return ExtractionResult(watermark=watermark, metadata={"method": self.method_name, "blind": True, "subband": self.subband})
