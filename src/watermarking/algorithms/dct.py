from __future__ import annotations

import cv2
import numpy as np

from watermarking.algorithms.base import ExtractionResult, Watermarker, WatermarkResult, ensure_grayscale_float, normalize_uint8, watermark_to_bits


class DCTWatermarker(Watermarker):
    method_name = "dct"

    def __init__(self, delta: float = 12.0, block_size: int = 8, coeff_pair: tuple[tuple[int, int], tuple[int, int]] = ((3, 4), (4, 3)), **params) -> None:
        super().__init__(delta=delta, block_size=block_size, coeff_pair=coeff_pair, **params)
        self.delta = float(delta)
        self.block_size = int(block_size)
        self.coeff_pair = tuple(tuple(pair) for pair in coeff_pair)

    def _capacity(self, image_shape: tuple[int, int]) -> int:
        return (image_shape[0] // self.block_size) * (image_shape[1] // self.block_size)

    def _iter_blocks(self, image: np.ndarray):
        height, width = image.shape
        for y in range(0, height - self.block_size + 1, self.block_size):
            for x in range(0, width - self.block_size + 1, self.block_size):
                yield y, x, image[y : y + self.block_size, x : x + self.block_size]

    def embed(self, image: np.ndarray, watermark: np.ndarray) -> WatermarkResult:
        host = ensure_grayscale_float(image).copy()
        bits = watermark_to_bits(watermark).ravel()
        if bits.size > self._capacity(host.shape):
            raise ValueError(f"Watermark has {bits.size} bits but DCT capacity is {self._capacity(host.shape)} bits.")
        c1, c2 = self.coeff_pair
        for bit, (y, x, block) in zip(bits, self._iter_blocks(host)):
            dct_block = cv2.dct(block.astype(np.float32))
            a = dct_block[c1]
            b = dct_block[c2]
            midpoint = (a + b) / 2.0
            if bit == 1:
                dct_block[c1] = midpoint + self.delta / 2.0
                dct_block[c2] = midpoint - self.delta / 2.0
            else:
                dct_block[c1] = midpoint - self.delta / 2.0
                dct_block[c2] = midpoint + self.delta / 2.0
            host[y : y + self.block_size, x : x + self.block_size] = cv2.idct(dct_block)
        return WatermarkResult(
            image=normalize_uint8(host),
            watermark=(bits.reshape(watermark.shape) * 255).astype(np.uint8),
            metadata={"method": self.method_name, "delta": self.delta, "blind": True},
        )

    def extract(self, image: np.ndarray, watermark_shape: tuple[int, int], original_image: np.ndarray | None = None) -> ExtractionResult:
        host = ensure_grayscale_float(image)
        total_bits = int(np.prod(watermark_shape))
        if total_bits > self._capacity(host.shape):
            raise ValueError(f"Watermark needs {total_bits} bits but DCT capacity is {self._capacity(host.shape)} bits.")
        c1, c2 = self.coeff_pair
        bits: list[int] = []
        for _, _, block in self._iter_blocks(host):
            dct_block = cv2.dct(block.astype(np.float32))
            bits.append(1 if dct_block[c1] > dct_block[c2] else 0)
            if len(bits) == total_bits:
                break
        watermark = (np.array(bits, dtype=np.uint8).reshape(watermark_shape) * 255).astype(np.uint8)
        return ExtractionResult(watermark=watermark, metadata={"method": self.method_name, "blind": True})
