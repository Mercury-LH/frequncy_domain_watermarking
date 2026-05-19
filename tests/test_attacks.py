import numpy as np

from watermarking.attacks import apply_attack, gaussian_noise, jpeg_compress, resize_attack


def test_jpeg_compress_preserves_shape_and_dtype():
    image = np.full((32, 32), 128, dtype=np.uint8)
    attacked = jpeg_compress(image, quality=50)
    assert attacked.shape == image.shape
    assert attacked.dtype == np.uint8


def test_resize_attack_restores_original_shape():
    image = np.full((40, 30), 128, dtype=np.uint8)
    attacked = resize_attack(image, scale=0.5)
    assert attacked.shape == image.shape


def test_gaussian_noise_is_deterministic_with_seed():
    image = np.full((16, 16), 128, dtype=np.uint8)
    first = gaussian_noise(image, sigma=5, seed=123)
    second = gaussian_noise(image, sigma=5, seed=123)
    assert np.array_equal(first, second)


def test_apply_attack_dispatches_jpeg():
    image = np.full((16, 16), 128, dtype=np.uint8)
    attacked = apply_attack(image, "jpeg", quality=80)
    assert attacked.shape == image.shape
