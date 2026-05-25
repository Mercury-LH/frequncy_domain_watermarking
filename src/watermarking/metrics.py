from __future__ import annotations

import math

import numpy as np
from skimage.metrics import structural_similarity


def _same_shape(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if a.shape != b.shape:
        raise ValueError(f"Shape mismatch: {a.shape} != {b.shape}.")
    return a.astype(np.float64, copy=False), b.astype(np.float64, copy=False)


def mse(reference: np.ndarray, candidate: np.ndarray) -> float:
    ref, cand = _same_shape(reference, candidate)
    return float(np.mean((ref - cand) ** 2))


def psnr(reference: np.ndarray, candidate: np.ndarray, data_range: float = 255.0) -> float:
    error = mse(reference, candidate)
    if error == 0:
        return math.inf
    return float(10 * math.log10((data_range**2) / error))


def ssim_score(reference: np.ndarray, candidate: np.ndarray, data_range: float = 255.0) -> float:
    if reference.shape != candidate.shape:
        raise ValueError(f"Shape mismatch: {reference.shape} != {candidate.shape}.")
    return float(structural_similarity(reference, candidate, data_range=data_range))


def _bits(array: np.ndarray) -> np.ndarray:
    return (array > 0).astype(np.uint8)


def bit_error_rate(reference: np.ndarray, candidate: np.ndarray) -> float:
    ref, cand = _same_shape(_bits(reference), _bits(candidate))
    return float(np.mean(ref != cand))


def normalized_correlation(reference: np.ndarray, candidate: np.ndarray) -> float:
    ref, cand = _same_shape(_bits(reference), _bits(candidate))
    ref = ref.astype(np.float64) * 2 - 1
    cand = cand.astype(np.float64) * 2 - 1
    denominator = np.linalg.norm(ref) * np.linalg.norm(cand)
    if denominator == 0:
        return 0.0
    return float(np.clip(np.sum(ref * cand) / denominator, -1.0, 1.0))


def _quality_input(image: np.ndarray) -> np.ndarray:
    if image.ndim == 3:
        return np.mean(image.astype(np.float64), axis=2)
    return image


def image_quality(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float]:
    reference_quality = _quality_input(reference)
    candidate_quality = _quality_input(candidate)
    return {
        "mse": mse(reference_quality, candidate_quality),
        "psnr": psnr(reference_quality, candidate_quality),
        "ssim": ssim_score(reference_quality, candidate_quality),
    }


def watermark_quality(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float]:
    return {
        "nc": normalized_correlation(reference, candidate),
        "ber": bit_error_rate(reference, candidate),
    }
