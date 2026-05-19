from pathlib import Path

import numpy as np

from watermarking.io_utils import ensure_demo_data, prepare_watermark, read_grayscale, save_grayscale


def test_save_and_read_grayscale_roundtrip(tmp_path):
    image = np.arange(64, dtype=np.uint8).reshape(8, 8)
    path = tmp_path / "image.png"
    save_grayscale(path, image)
    loaded = read_grayscale(path)
    assert loaded.shape == image.shape
    assert loaded.dtype == np.uint8


def test_prepare_watermark_resizes_and_binarizes():
    watermark = np.array([[0, 255], [128, 64]], dtype=np.uint8)
    prepared = prepare_watermark(watermark, (4, 4))
    assert prepared.shape == (4, 4)
    assert set(np.unique(prepared)).issubset({0, 255})


def test_ensure_demo_data_creates_files_when_download_is_unavailable(tmp_path):
    image_path = tmp_path / "raw" / "lena.png"
    watermark_path = tmp_path / "watermark" / "logo.png"
    ensure_demo_data(image_path, watermark_path, allow_download=False)
    assert image_path.exists()
    assert watermark_path.exists()
