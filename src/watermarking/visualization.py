from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _save(path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    plt.close()


def _imshow(axis, image: np.ndarray) -> None:
    if image.ndim == 3:
        axis.imshow(np.clip(image, 0, 255).astype(np.uint8))
    else:
        axis.imshow(image, cmap="gray")


def save_comparison_figure(path: str | Path, original: np.ndarray, watermarked: np.ndarray, watermark: np.ndarray, extracted: np.ndarray, title: str) -> None:
    difference = np.abs(original.astype(np.float64) - watermarked.astype(np.float64))
    if difference.ndim == 3:
        difference = np.mean(difference, axis=2)
    fig, axes = plt.subplots(1, 5, figsize=(14, 3))
    items = [(original, "Original"), (watermarked, "Watermarked"), (difference, "Difference"), (watermark, "Watermark"), (extracted, "Extracted")]
    for axis, (image, label) in zip(axes, items):
        _imshow(axis, image)
        axis.set_title(label)
        axis.axis("off")
    fig.suptitle(title)
    _save(path)


def save_spectrum_figure(path: str | Path, image: np.ndarray) -> None:
    spectrum = np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(image))))
    plt.figure(figsize=(5, 4))
    plt.imshow(spectrum, cmap="magma")
    plt.title("Log Magnitude Spectrum")
    plt.axis("off")
    _save(path)


def save_metric_curve(path: str | Path, data: pd.DataFrame, x: str, y: str, hue: str, title: str) -> None:
    plt.figure(figsize=(6, 4))
    for label, group in data.groupby(hue):
        plt.plot(group[x], group[y], marker="o", label=str(label))
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()
    _save(path)
