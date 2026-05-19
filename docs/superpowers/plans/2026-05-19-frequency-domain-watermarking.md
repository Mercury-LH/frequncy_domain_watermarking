# Frequency Domain Watermarking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a modular image frequency-domain watermarking project that implements DFT, DCT, and DWT watermarking plus strength and robustness experiments.

**Architecture:** Use a small research-style Python package under `src/watermarking` with a common algorithm interface, separate attack/metric/visualization utilities, CLI entrypoint, YAML-driven experiments, and one-command experiment scripts. DFT covers the required non-blind baseline; DCT and DWT provide blind or semi-blind challenge algorithms.

**Tech Stack:** Python 3.10+, NumPy, OpenCV, SciPy, scikit-image, matplotlib, PyWavelets, PyYAML, pandas, pytest.

---

## File Structure

- Create `requirements.txt` — pinned runtime and test dependencies.
- Create `pyproject.toml` — pytest path configuration and package metadata.
- Create `configs/experiments.yaml` — default data paths, algorithm parameters, and experiment sweeps.
- Create `src/watermarking/__init__.py` — package export marker.
- Create `src/watermarking/algorithms/__init__.py` — algorithm package exports.
- Create `src/watermarking/algorithms/base.py` — shared dataclasses and abstract watermarker interface.
- Create `src/watermarking/algorithms/dft.py` — DFT non-blind embedding/extraction.
- Create `src/watermarking/algorithms/dct.py` — DCT blind block-based embedding/extraction.
- Create `src/watermarking/algorithms/dwt.py` — DWT blind/semi-blind embedding/extraction.
- Create `src/watermarking/registry.py` — `dft|dct|dwt` name-to-class factory.
- Create `src/watermarking/io_utils.py` — image loading, saving, watermark preparation, demo dataset download/generation.
- Create `src/watermarking/metrics.py` — MSE, PSNR, SSIM, NC, BER.
- Create `src/watermarking/attacks.py` — JPEG, resize, Gaussian noise, blur, crop attacks.
- Create `src/watermarking/visualization.py` — comparison figures, spectra, metric plots.
- Create `main.py` — CLI for embed/extract/attack.
- Create `experiments/run_basic.py` — basic embed/extract for all methods.
- Create `experiments/run_strength.py` — strength sweep experiment.
- Create `experiments/run_attacks.py` — robustness experiment.
- Create `experiments/run_all.py` — calls all experiment scripts.
- Create `tests/` files for metrics, attacks, registry, algorithm smoke tests, CLI smoke tests.
- Create `README.md` — setup, quickstart, algorithms, experiments, expected outputs.
- Modify `task_plan.md` and `progress.md` — update phase status and implementation progress.

---

### Task 1: Project Scaffold and Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `pyproject.toml`
- Create: `configs/experiments.yaml`
- Create: `src/watermarking/__init__.py`
- Create: `src/watermarking/algorithms/__init__.py`
- Create: `tests/test_scaffold.py`

- [ ] **Step 1: Write the failing scaffold test**

Create `tests/test_scaffold.py`:

```python
from pathlib import Path


def test_project_scaffold_files_exist():
    expected = [
        Path("requirements.txt"),
        Path("pyproject.toml"),
        Path("configs/experiments.yaml"),
        Path("src/watermarking/__init__.py"),
        Path("src/watermarking/algorithms/__init__.py"),
    ]
    missing = [str(path) for path in expected if not path.exists()]
    assert missing == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_scaffold.py -v`

Expected: FAIL because scaffold files do not exist yet.

- [ ] **Step 3: Create dependencies and package config**

Create `requirements.txt`:

```text
numpy==1.26.4
opencv-python==4.9.0.80
scipy==1.12.0
scikit-image==0.22.0
matplotlib==3.8.3
PyWavelets==1.5.0
PyYAML==6.0.1
pandas==2.2.1
requests==2.31.0
pytest==8.0.2
```

Create `pyproject.toml`:

```toml
[project]
name = "frequency-domain-watermarking"
version = "0.1.0"
description = "Frequency-domain image watermarking experiments for DFT, DCT, and DWT."
requires-python = ">=3.10"

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

Create `configs/experiments.yaml`:

```yaml
dataset:
  image: data/raw/lena.png
  watermark: data/watermark/logo.png
  image_size: [512, 512]

output:
  root: outputs

methods:
  dft:
    alpha: 10.0
    watermark_size: [64, 64]
    radius_ratio: 0.28
  dct:
    delta: 12.0
    block_size: 8
    watermark_size: [32, 32]
    coeff_pair: [[3, 4], [4, 3]]
  dwt:
    alpha: 0.05
    wavelet: haar
    subband: hl
    watermark_size: [64, 64]

experiments:
  methods: [dft, dct, dwt]
  strengths:
    dft: [2, 5, 10, 20, 40]
    dct: [2, 5, 10, 20, 40]
    dwt: [0.01, 0.03, 0.05, 0.1]
  jpeg_qualities: [90, 70, 50, 30]
  noise_sigmas: [5, 10, 20]
  scale_factors: [0.5, 0.75, 1.5]
```

Create empty package markers:

```bash
mkdir -p configs src/watermarking/algorithms tests
: > src/watermarking/__init__.py
: > src/watermarking/algorithms/__init__.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_scaffold.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt pyproject.toml configs/experiments.yaml src/watermarking/__init__.py src/watermarking/algorithms/__init__.py tests/test_scaffold.py
git commit -m "chore: scaffold watermarking project"
```

---

### Task 2: Shared Algorithm Interface and Registry

**Files:**
- Create: `src/watermarking/algorithms/base.py`
- Create: `src/watermarking/registry.py`
- Modify: `src/watermarking/algorithms/__init__.py`
- Create: `tests/test_registry.py`

- [ ] **Step 1: Write failing interface and registry tests**

Create `tests/test_registry.py`:

```python
import numpy as np
import pytest

from watermarking.algorithms.base import ExtractionResult, WatermarkResult
from watermarking.registry import create_watermarker, list_methods


def test_result_dataclasses_store_arrays_and_metadata():
    image = np.zeros((8, 8), dtype=np.uint8)
    watermark = np.ones((2, 2), dtype=np.uint8)
    embedded = WatermarkResult(image=image, watermark=watermark, metadata={"method": "x"})
    extracted = ExtractionResult(watermark=watermark, metadata={"blind": True})
    assert embedded.metadata["method"] == "x"
    assert extracted.metadata["blind"] is True


def test_registry_lists_expected_methods():
    assert list_methods() == ["dct", "dft", "dwt"]


def test_registry_rejects_unknown_method():
    with pytest.raises(ValueError, match="Unknown watermarking method"):
        create_watermarker("unknown")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_registry.py -v`

Expected: FAIL because `base.py` and `registry.py` do not exist.

- [ ] **Step 3: Implement base interface**

Create `src/watermarking/algorithms/base.py`:

```python
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
```

- [ ] **Step 4: Add temporary algorithm classes and registry**

Create `src/watermarking/registry.py`:

```python
from __future__ import annotations

from typing import Any

from watermarking.algorithms.base import ExtractionResult, Watermarker, WatermarkResult


class _PlaceholderWatermarker(Watermarker):
    method_name = "placeholder"

    def embed(self, image, watermark) -> WatermarkResult:
        raise NotImplementedError("Algorithm implementation is added in later tasks.")

    def extract(self, image, watermark_shape, original_image=None) -> ExtractionResult:
        raise NotImplementedError("Algorithm implementation is added in later tasks.")


_REGISTRY: dict[str, type[Watermarker]] = {
    "dct": _PlaceholderWatermarker,
    "dft": _PlaceholderWatermarker,
    "dwt": _PlaceholderWatermarker,
}


def list_methods() -> list[str]:
    return sorted(_REGISTRY)


def create_watermarker(method: str, **params: Any) -> Watermarker:
    key = method.lower()
    if key not in _REGISTRY:
        available = ", ".join(list_methods())
        raise ValueError(f"Unknown watermarking method '{method}'. Available methods: {available}.")
    return _REGISTRY[key](**params)
```

Modify `src/watermarking/algorithms/__init__.py`:

```python
from watermarking.algorithms.base import ExtractionResult, Watermarker, WatermarkResult

__all__ = ["ExtractionResult", "Watermarker", "WatermarkResult"]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_registry.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/watermarking/algorithms/base.py src/watermarking/algorithms/__init__.py src/watermarking/registry.py tests/test_registry.py
git commit -m "feat: add watermarking interface and registry"
```

---

### Task 3: Metrics Utilities

**Files:**
- Create: `src/watermarking/metrics.py`
- Create: `tests/test_metrics.py`

- [ ] **Step 1: Write failing metric tests**

Create `tests/test_metrics.py`:

```python
import math

import numpy as np

from watermarking.metrics import bit_error_rate, mse, normalized_correlation, psnr, ssim_score


def test_mse_and_psnr_for_identical_images():
    image = np.full((8, 8), 128, dtype=np.uint8)
    assert mse(image, image) == 0.0
    assert math.isinf(psnr(image, image))


def test_bit_error_rate_counts_different_bits():
    expected = np.array([[0, 1], [1, 0]], dtype=np.uint8)
    actual = np.array([[0, 0], [1, 1]], dtype=np.uint8)
    assert bit_error_rate(expected, actual) == 0.5


def test_normalized_correlation_identical_watermarks():
    watermark = np.array([[0, 255], [255, 0]], dtype=np.uint8)
    assert normalized_correlation(watermark, watermark) == 1.0


def test_ssim_identical_images():
    image = np.full((16, 16), 127, dtype=np.uint8)
    assert ssim_score(image, image) == 1.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_metrics.py -v`

Expected: FAIL because `metrics.py` does not exist.

- [ ] **Step 3: Implement metrics**

Create `src/watermarking/metrics.py`:

```python
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
    return (array > 127).astype(np.uint8)


def bit_error_rate(reference: np.ndarray, candidate: np.ndarray) -> float:
    ref, cand = _same_shape(_bits(reference), _bits(candidate))
    return float(np.mean(ref != cand))


def normalized_correlation(reference: np.ndarray, candidate: np.ndarray) -> float:
    ref, cand = _same_shape(_bits(reference), _bits(candidate))
    ref = ref * 2 - 1
    cand = cand * 2 - 1
    denominator = np.linalg.norm(ref) * np.linalg.norm(cand)
    if denominator == 0:
        return 0.0
    return float(np.clip(np.sum(ref * cand) / denominator, -1.0, 1.0))


def image_quality(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float]:
    return {
        "mse": mse(reference, candidate),
        "psnr": psnr(reference, candidate),
        "ssim": ssim_score(reference, candidate),
    }


def watermark_quality(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float]:
    return {
        "nc": normalized_correlation(reference, candidate),
        "ber": bit_error_rate(reference, candidate),
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_metrics.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/watermarking/metrics.py tests/test_metrics.py
git commit -m "feat: add watermarking metrics"
```

---

### Task 4: IO Utilities and Demo Data Preparation

**Files:**
- Create: `src/watermarking/io_utils.py`
- Create: `tests/test_io_utils.py`

- [ ] **Step 1: Write failing IO tests**

Create `tests/test_io_utils.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_io_utils.py -v`

Expected: FAIL because `io_utils.py` does not exist.

- [ ] **Step 3: Implement IO utilities**

Create `src/watermarking/io_utils.py`:

```python
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


def save_grayscale(path: str | Path, image: np.ndarray) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ok = cv2.imwrite(str(output_path), np.clip(image, 0, 255).astype(np.uint8))
    if not ok:
        raise ValueError(f"Failed to save image: {output_path}.")


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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_io_utils.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/watermarking/io_utils.py tests/test_io_utils.py
git commit -m "feat: add image IO and demo data utilities"
```

---

### Task 5: Attack Utilities

**Files:**
- Create: `src/watermarking/attacks.py`
- Create: `tests/test_attacks.py`

- [ ] **Step 1: Write failing attack tests**

Create `tests/test_attacks.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_attacks.py -v`

Expected: FAIL because `attacks.py` does not exist.

- [ ] **Step 3: Implement attacks**

Create `src/watermarking/attacks.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_attacks.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/watermarking/attacks.py tests/test_attacks.py
git commit -m "feat: add watermark attack utilities"
```

---

### Task 6: DFT Non-Blind Watermarker

**Files:**
- Create: `src/watermarking/algorithms/dft.py`
- Modify: `src/watermarking/registry.py`
- Modify: `src/watermarking/algorithms/__init__.py`
- Create: `tests/test_dft_watermarker.py`

- [ ] **Step 1: Write failing DFT tests**

Create `tests/test_dft_watermarker.py`:

```python
import numpy as np
import pytest

from watermarking.algorithms.dft import DFTWatermarker
from watermarking.metrics import bit_error_rate, psnr


def test_dft_embed_extract_recovers_watermark_with_original():
    rng = np.random.default_rng(7)
    image = rng.integers(30, 220, size=(128, 128), dtype=np.uint8)
    watermark = rng.choice([0, 255], size=(16, 16)).astype(np.uint8)
    watermarker = DFTWatermarker(alpha=30.0, radius_ratio=0.25)

    embedded = watermarker.embed(image, watermark)
    extracted = watermarker.extract(embedded.image, watermark.shape, original_image=image)

    assert embedded.image.shape == image.shape
    assert psnr(image, embedded.image) > 20
    assert bit_error_rate(watermark, extracted.watermark) < 0.05


def test_dft_extract_requires_original_image():
    image = np.full((64, 64), 128, dtype=np.uint8)
    watermarker = DFTWatermarker(alpha=10.0)
    with pytest.raises(ValueError, match="requires original_image"):
        watermarker.extract(image, (8, 8))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_dft_watermarker.py -v`

Expected: FAIL because `dft.py` does not exist.

- [ ] **Step 3: Implement DFT watermarker**

Create `src/watermarking/algorithms/dft.py`:

```python
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
        for idx, (y, x) in enumerate(positions):
            value = self.alpha * flat_signs[idx]
            spectrum[y, x] += value
            spectrum[(height - y) % height, (width - x) % width] += value
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
        difference = np.fft.fftshift(np.fft.fft2(watermarked)) - np.fft.fftshift(np.fft.fft2(original))
        positions = self._positions(watermarked.shape, watermark_shape)
        bits = np.array([1 if difference[y, x].real >= 0 else 0 for y, x in positions], dtype=np.uint8)
        watermark = (bits.reshape(watermark_shape) * 255).astype(np.uint8)
        return ExtractionResult(watermark=watermark, metadata={"method": self.method_name, "blind": False})
```

- [ ] **Step 4: Register DFT implementation**

Modify `src/watermarking/registry.py`:

```python
from __future__ import annotations

from typing import Any

from watermarking.algorithms.base import Watermarker
from watermarking.algorithms.dft import DFTWatermarker


class _PlaceholderWatermarker(Watermarker):
    method_name = "placeholder"

    def embed(self, image, watermark):
        raise NotImplementedError("Algorithm implementation is added in later tasks.")

    def extract(self, image, watermark_shape, original_image=None):
        raise NotImplementedError("Algorithm implementation is added in later tasks.")


_REGISTRY: dict[str, type[Watermarker]] = {
    "dct": _PlaceholderWatermarker,
    "dft": DFTWatermarker,
    "dwt": _PlaceholderWatermarker,
}


def list_methods() -> list[str]:
    return sorted(_REGISTRY)


def create_watermarker(method: str, **params: Any) -> Watermarker:
    key = method.lower()
    if key not in _REGISTRY:
        available = ", ".join(list_methods())
        raise ValueError(f"Unknown watermarking method '{method}'. Available methods: {available}.")
    return _REGISTRY[key](**params)
```

Modify `src/watermarking/algorithms/__init__.py`:

```python
from watermarking.algorithms.base import ExtractionResult, Watermarker, WatermarkResult
from watermarking.algorithms.dft import DFTWatermarker

__all__ = ["DFTWatermarker", "ExtractionResult", "Watermarker", "WatermarkResult"]
```

- [ ] **Step 5: Run DFT tests**

Run: `python -m pytest tests/test_dft_watermarker.py tests/test_registry.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/watermarking/algorithms/dft.py src/watermarking/registry.py src/watermarking/algorithms/__init__.py tests/test_dft_watermarker.py
git commit -m "feat: add DFT non-blind watermarker"
```

---

### Task 7: DCT Blind Watermarker

**Files:**
- Create: `src/watermarking/algorithms/dct.py`
- Modify: `src/watermarking/registry.py`
- Modify: `src/watermarking/algorithms/__init__.py`
- Create: `tests/test_dct_watermarker.py`

- [ ] **Step 1: Write failing DCT tests**

Create `tests/test_dct_watermarker.py`:

```python
import numpy as np

from watermarking.algorithms.dct import DCTWatermarker
from watermarking.metrics import bit_error_rate, psnr


def test_dct_blind_embed_extract_recovers_watermark_without_original():
    rng = np.random.default_rng(11)
    image = rng.integers(20, 230, size=(128, 128), dtype=np.uint8)
    watermark = rng.choice([0, 255], size=(8, 8)).astype(np.uint8)
    watermarker = DCTWatermarker(delta=28.0, block_size=8)

    embedded = watermarker.embed(image, watermark)
    extracted = watermarker.extract(embedded.image, watermark.shape)

    assert embedded.image.shape == image.shape
    assert embedded.metadata["blind"] is True
    assert psnr(image, embedded.image) > 20
    assert bit_error_rate(watermark, extracted.watermark) < 0.1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_dct_watermarker.py -v`

Expected: FAIL because `dct.py` does not exist.

- [ ] **Step 3: Implement DCT watermarker**

Create `src/watermarking/algorithms/dct.py`:

```python
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
        self.coeff_pair = coeff_pair

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
```

- [ ] **Step 4: Register DCT implementation**

Modify `src/watermarking/registry.py` imports and registry:

```python
from watermarking.algorithms.dct import DCTWatermarker
from watermarking.algorithms.dft import DFTWatermarker
```

Set `_REGISTRY` to:

```python
_REGISTRY: dict[str, type[Watermarker]] = {
    "dct": DCTWatermarker,
    "dft": DFTWatermarker,
    "dwt": _PlaceholderWatermarker,
}
```

Modify `src/watermarking/algorithms/__init__.py`:

```python
from watermarking.algorithms.base import ExtractionResult, Watermarker, WatermarkResult
from watermarking.algorithms.dct import DCTWatermarker
from watermarking.algorithms.dft import DFTWatermarker

__all__ = ["DCTWatermarker", "DFTWatermarker", "ExtractionResult", "Watermarker", "WatermarkResult"]
```

- [ ] **Step 5: Run DCT tests**

Run: `python -m pytest tests/test_dct_watermarker.py tests/test_registry.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/watermarking/algorithms/dct.py src/watermarking/registry.py src/watermarking/algorithms/__init__.py tests/test_dct_watermarker.py
git commit -m "feat: add DCT blind watermarker"
```

---

### Task 8: DWT Watermarker

**Files:**
- Create: `src/watermarking/algorithms/dwt.py`
- Modify: `src/watermarking/registry.py`
- Modify: `src/watermarking/algorithms/__init__.py`
- Create: `tests/test_dwt_watermarker.py`

- [ ] **Step 1: Write failing DWT tests**

Create `tests/test_dwt_watermarker.py`:

```python
import numpy as np

from watermarking.algorithms.dwt import DWTWatermarker
from watermarking.metrics import bit_error_rate, psnr


def test_dwt_blind_embed_extract_recovers_watermark():
    rng = np.random.default_rng(17)
    image = rng.integers(20, 230, size=(128, 128), dtype=np.uint8)
    watermark = rng.choice([0, 255], size=(16, 16)).astype(np.uint8)
    watermarker = DWTWatermarker(alpha=8.0, wavelet="haar", subband="hl")

    embedded = watermarker.embed(image, watermark)
    extracted = watermarker.extract(embedded.image, watermark.shape)

    assert embedded.image.shape == image.shape
    assert embedded.metadata["blind"] is True
    assert psnr(image, embedded.image) > 18
    assert bit_error_rate(watermark, extracted.watermark) < 0.2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_dwt_watermarker.py -v`

Expected: FAIL because `dwt.py` does not exist.

- [ ] **Step 3: Implement DWT watermarker**

Create `src/watermarking/algorithms/dwt.py`:

```python
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
        coeffs = pywt.dwt2(host, self.wavelet)
        ll, bands = coeffs
        selected = self._select_subband(bands).copy()
        if bits.shape[0] > selected.shape[0] or bits.shape[1] > selected.shape[1]:
            raise ValueError(f"Watermark shape {bits.shape} exceeds DWT subband capacity {selected.shape}.")
        patch = selected[: bits.shape[0], : bits.shape[1]]
        signs = bits.astype(np.float64) * 2 - 1
        scale = self.alpha * max(float(np.std(selected)), 1.0)
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
```

- [ ] **Step 4: Register DWT implementation**

Modify `src/watermarking/registry.py` imports and registry:

```python
from watermarking.algorithms.dct import DCTWatermarker
from watermarking.algorithms.dft import DFTWatermarker
from watermarking.algorithms.dwt import DWTWatermarker
```

Set `_REGISTRY` to:

```python
_REGISTRY: dict[str, type[Watermarker]] = {
    "dct": DCTWatermarker,
    "dft": DFTWatermarker,
    "dwt": DWTWatermarker,
}
```

Modify `src/watermarking/algorithms/__init__.py`:

```python
from watermarking.algorithms.base import ExtractionResult, Watermarker, WatermarkResult
from watermarking.algorithms.dct import DCTWatermarker
from watermarking.algorithms.dft import DFTWatermarker
from watermarking.algorithms.dwt import DWTWatermarker

__all__ = ["DCTWatermarker", "DFTWatermarker", "DWTWatermarker", "ExtractionResult", "Watermarker", "WatermarkResult"]
```

- [ ] **Step 5: Run DWT tests**

Run: `python -m pytest tests/test_dwt_watermarker.py tests/test_registry.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/watermarking/algorithms/dwt.py src/watermarking/registry.py src/watermarking/algorithms/__init__.py tests/test_dwt_watermarker.py
git commit -m "feat: add DWT watermarker"
```

---

### Task 9: Visualization Utilities

**Files:**
- Create: `src/watermarking/visualization.py`
- Create: `tests/test_visualization.py`

- [ ] **Step 1: Write failing visualization tests**

Create `tests/test_visualization.py`:

```python
from pathlib import Path

import numpy as np
import pandas as pd

from watermarking.visualization import save_comparison_figure, save_metric_curve, save_spectrum_figure


def test_visualization_writes_expected_files(tmp_path):
    image = np.full((32, 32), 128, dtype=np.uint8)
    watermark = np.zeros((8, 8), dtype=np.uint8)
    comparison = tmp_path / "comparison.png"
    spectrum = tmp_path / "spectrum.png"
    curve = tmp_path / "curve.png"
    save_comparison_figure(comparison, image, image, watermark, watermark, title="demo")
    save_spectrum_figure(spectrum, image)
    save_metric_curve(curve, pd.DataFrame({"strength": [1, 2], "psnr": [30, 25], "method": ["dft", "dft"]}), x="strength", y="psnr", hue="method", title="curve")
    assert comparison.exists()
    assert spectrum.exists()
    assert curve.exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_visualization.py -v`

Expected: FAIL because `visualization.py` does not exist.

- [ ] **Step 3: Implement visualization utilities**

Create `src/watermarking/visualization.py`:

```python
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


def save_comparison_figure(path: str | Path, original: np.ndarray, watermarked: np.ndarray, watermark: np.ndarray, extracted: np.ndarray, title: str) -> None:
    difference = np.abs(original.astype(np.float64) - watermarked.astype(np.float64))
    fig, axes = plt.subplots(1, 5, figsize=(14, 3))
    items = [(original, "Original"), (watermarked, "Watermarked"), (difference, "Difference"), (watermark, "Watermark"), (extracted, "Extracted")]
    for axis, (image, label) in zip(axes, items):
        axis.imshow(image, cmap="gray")
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_visualization.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/watermarking/visualization.py tests/test_visualization.py
git commit -m "feat: add experiment visualization utilities"
```

---

### Task 10: CLI Entrypoint

**Files:**
- Create: `main.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Create `tests/test_cli.py`:

```python
import subprocess
import sys


def test_cli_help_runs():
    result = subprocess.run([sys.executable, "main.py", "--help"], text=True, capture_output=True, check=False)
    assert result.returncode == 0
    assert "embed" in result.stdout
    assert "extract" in result.stdout
    assert "attack" in result.stdout
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_cli.py -v`

Expected: FAIL because `main.py` does not exist or lacks commands.

- [ ] **Step 3: Implement CLI**

Create `main.py`:

```python
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from watermarking.attacks import apply_attack
from watermarking.io_utils import prepare_watermark, read_grayscale, save_grayscale
from watermarking.registry import create_watermarker, list_methods


def load_config(path: str | None) -> dict:
    if path is None:
        return {}
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def method_params(config: dict, method: str) -> dict:
    return dict(config.get("methods", {}).get(method, {}))


def command_embed(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    params = method_params(config, args.method)
    params.update(args.param or {})
    image = read_grayscale(args.image)
    watermark = read_grayscale(args.watermark)
    shape = tuple(params.pop("watermark_size", watermark.shape))
    prepared = prepare_watermark(watermark, (int(shape[0]), int(shape[1])))
    watermarker = create_watermarker(args.method, **params)
    result = watermarker.embed(image, prepared)
    save_grayscale(args.output, result.image)
    print(f"Saved watermarked image to {args.output}")


def command_extract(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    params = method_params(config, args.method)
    shape = tuple(params.pop("watermark_size", args.watermark_size))
    image = read_grayscale(args.image)
    original = read_grayscale(args.original) if args.original else None
    watermarker = create_watermarker(args.method, **params)
    result = watermarker.extract(image, (int(shape[0]), int(shape[1])), original_image=original)
    save_grayscale(args.output, result.watermark)
    print(f"Saved extracted watermark to {args.output}")


def command_attack(args: argparse.Namespace) -> None:
    image = read_grayscale(args.image)
    params = {"quality": args.quality, "scale": args.scale, "sigma": args.sigma, "kernel_size": args.kernel_size, "ratio": args.ratio}
    attacked = apply_attack(image, args.type, **{k: v for k, v in params.items() if v is not None})
    save_grayscale(args.output, attacked)
    print(f"Saved attacked image to {args.output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Frequency-domain image watermarking")
    subparsers = parser.add_subparsers(dest="command", required=True)

    embed = subparsers.add_parser("embed")
    embed.add_argument("--method", required=True, choices=list_methods())
    embed.add_argument("--image", required=True)
    embed.add_argument("--watermark", required=True)
    embed.add_argument("--output", required=True)
    embed.add_argument("--config", default="configs/experiments.yaml")
    embed.set_defaults(func=command_embed, param={})

    extract = subparsers.add_parser("extract")
    extract.add_argument("--method", required=True, choices=list_methods())
    extract.add_argument("--image", required=True)
    extract.add_argument("--original")
    extract.add_argument("--output", required=True)
    extract.add_argument("--watermark-size", nargs=2, type=int, default=(64, 64))
    extract.add_argument("--config", default="configs/experiments.yaml")
    extract.set_defaults(func=command_extract)

    attack = subparsers.add_parser("attack")
    attack.add_argument("--type", required=True, choices=["jpeg", "resize", "noise", "blur", "crop"])
    attack.add_argument("--image", required=True)
    attack.add_argument("--output", required=True)
    attack.add_argument("--quality", type=int)
    attack.add_argument("--scale", type=float)
    attack.add_argument("--sigma", type=float)
    attack.add_argument("--kernel-size", type=int)
    attack.add_argument("--ratio", type=float)
    attack.set_defaults(func=command_attack)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run CLI tests**

Run: `python -m pytest tests/test_cli.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add main.py tests/test_cli.py
git commit -m "feat: add watermarking CLI"
```

---

### Task 11: Basic Experiment Script

**Files:**
- Create: `experiments/run_basic.py`
- Create: `tests/test_run_basic.py`

- [ ] **Step 1: Write failing basic experiment test**

Create `tests/test_run_basic.py`:

```python
from pathlib import Path

from experiments.run_basic import run_basic


def test_run_basic_creates_outputs(tmp_path):
    output_root = tmp_path / "outputs"
    rows = run_basic(output_root=output_root, allow_download=False, methods=["dft", "dct"])
    assert len(rows) == 2
    assert (output_root / "basic" / "metrics_basic.csv").exists()
    assert any((output_root / "basic").glob("*_watermarked.png"))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_run_basic.py -v`

Expected: FAIL because `experiments/run_basic.py` does not exist.

- [ ] **Step 3: Implement basic experiment**

Create `experiments/run_basic.py`:

```python
from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from watermarking.io_utils import ensure_demo_data, prepare_watermark, read_grayscale, save_grayscale
from watermarking.metrics import image_quality, watermark_quality
from watermarking.registry import create_watermarker
from watermarking.visualization import save_comparison_figure, save_spectrum_figure


def _load_config(config_path: str | Path = "configs/experiments.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def run_basic(output_root: str | Path = "outputs", allow_download: bool = True, methods: list[str] | None = None) -> list[dict]:
    config = _load_config()
    image_path = Path(config["dataset"]["image"])
    watermark_path = Path(config["dataset"]["watermark"])
    ensure_demo_data(image_path, watermark_path, allow_download=allow_download)
    image = read_grayscale(image_path)
    watermark_source = read_grayscale(watermark_path)
    output_dir = Path(output_root) / "basic"
    output_dir.mkdir(parents=True, exist_ok=True)
    selected_methods = methods or config["experiments"]["methods"]
    rows: list[dict] = []
    for method in selected_methods:
        params = dict(config["methods"][method])
        watermark_size = tuple(params.pop("watermark_size"))
        watermark = prepare_watermark(watermark_source, (int(watermark_size[0]), int(watermark_size[1])))
        watermarker = create_watermarker(method, **params)
        embedded = watermarker.embed(image, watermark)
        original_for_extract = image if method == "dft" else None
        extracted = watermarker.extract(embedded.image, watermark.shape, original_image=original_for_extract)
        watermarked_path = output_dir / f"{method}_watermarked.png"
        extracted_path = output_dir / f"{method}_extracted.png"
        comparison_path = output_dir / f"{method}_comparison.png"
        spectrum_path = output_dir / f"{method}_spectrum.png"
        save_grayscale(watermarked_path, embedded.image)
        save_grayscale(extracted_path, extracted.watermark)
        save_comparison_figure(comparison_path, image, embedded.image, watermark, extracted.watermark, title=f"{method.upper()} Basic Result")
        save_spectrum_figure(spectrum_path, embedded.image)
        row = {"method": method}
        row.update(image_quality(image, embedded.image))
        row.update(watermark_quality(watermark, extracted.watermark))
        rows.append(row)
    pd.DataFrame(rows).to_csv(output_dir / "metrics_basic.csv", index=False)
    return rows


if __name__ == "__main__":
    run_basic()
```

- [ ] **Step 4: Run basic experiment tests**

Run: `python -m pytest tests/test_run_basic.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/run_basic.py tests/test_run_basic.py
git commit -m "feat: add basic watermarking experiment"
```

---

### Task 12: Strength Experiment Script

**Files:**
- Create: `experiments/run_strength.py`
- Create: `tests/test_run_strength.py`

- [ ] **Step 1: Write failing strength experiment test**

Create `tests/test_run_strength.py`:

```python
from experiments.run_strength import run_strength


def test_run_strength_creates_metrics(tmp_path):
    rows = run_strength(output_root=tmp_path, allow_download=False, methods=["dft"], strengths={"dft": [5, 10]})
    assert len(rows) == 2
    assert (tmp_path / "strength" / "metrics_strength.csv").exists()
    assert (tmp_path / "strength" / "strength_psnr.png").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_run_strength.py -v`

Expected: FAIL because `experiments/run_strength.py` does not exist.

- [ ] **Step 3: Implement strength experiment**

Create `experiments/run_strength.py`:

```python
from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from watermarking.io_utils import ensure_demo_data, prepare_watermark, read_grayscale
from watermarking.metrics import image_quality, watermark_quality
from watermarking.registry import create_watermarker
from watermarking.visualization import save_metric_curve


def _load_config(config_path: str | Path = "configs/experiments.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _strength_key(method: str) -> str:
    return "delta" if method == "dct" else "alpha"


def run_strength(output_root: str | Path = "outputs", allow_download: bool = True, methods: list[str] | None = None, strengths: dict[str, list[float]] | None = None) -> list[dict]:
    config = _load_config()
    image_path = Path(config["dataset"]["image"])
    watermark_path = Path(config["dataset"]["watermark"])
    ensure_demo_data(image_path, watermark_path, allow_download=allow_download)
    image = read_grayscale(image_path)
    watermark_source = read_grayscale(watermark_path)
    output_dir = Path(output_root) / "strength"
    output_dir.mkdir(parents=True, exist_ok=True)
    selected_methods = methods or config["experiments"]["methods"]
    sweep = strengths or config["experiments"]["strengths"]
    rows: list[dict] = []
    for method in selected_methods:
        for value in sweep[method]:
            params = dict(config["methods"][method])
            watermark_size = tuple(params.pop("watermark_size"))
            params[_strength_key(method)] = value
            watermark = prepare_watermark(watermark_source, (int(watermark_size[0]), int(watermark_size[1])))
            watermarker = create_watermarker(method, **params)
            embedded = watermarker.embed(image, watermark)
            extracted = watermarker.extract(embedded.image, watermark.shape, original_image=image if method == "dft" else None)
            row = {"method": method, "strength": value}
            row.update(image_quality(image, embedded.image))
            row.update(watermark_quality(watermark, extracted.watermark))
            rows.append(row)
    frame = pd.DataFrame(rows)
    frame.to_csv(output_dir / "metrics_strength.csv", index=False)
    save_metric_curve(output_dir / "strength_psnr.png", frame, x="strength", y="psnr", hue="method", title="Embedding Strength vs PSNR")
    save_metric_curve(output_dir / "strength_ber.png", frame, x="strength", y="ber", hue="method", title="Embedding Strength vs BER")
    return rows


if __name__ == "__main__":
    run_strength()
```

- [ ] **Step 4: Run strength experiment tests**

Run: `python -m pytest tests/test_run_strength.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/run_strength.py tests/test_run_strength.py
git commit -m "feat: add embedding strength experiment"
```

---

### Task 13: Robustness Attack Experiment Script

**Files:**
- Create: `experiments/run_attacks.py`
- Create: `tests/test_run_attacks.py`

- [ ] **Step 1: Write failing attack experiment test**

Create `tests/test_run_attacks.py`:

```python
from experiments.run_attacks import run_attacks


def test_run_attacks_creates_metrics(tmp_path):
    rows = run_attacks(output_root=tmp_path, allow_download=False, methods=["dct"], jpeg_qualities=[80], noise_sigmas=[5], scale_factors=[0.75])
    assert len(rows) == 3
    assert (tmp_path / "attacks" / "metrics_attacks.csv").exists()
    assert (tmp_path / "attacks" / "attack_ber.png").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_run_attacks.py -v`

Expected: FAIL because `experiments/run_attacks.py` does not exist.

- [ ] **Step 3: Implement attack experiment**

Create `experiments/run_attacks.py`:

```python
from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from watermarking.attacks import gaussian_noise, jpeg_compress, resize_attack
from watermarking.io_utils import ensure_demo_data, prepare_watermark, read_grayscale, save_grayscale
from watermarking.metrics import image_quality, watermark_quality
from watermarking.registry import create_watermarker
from watermarking.visualization import save_metric_curve


def _load_config(config_path: str | Path = "configs/experiments.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def run_attacks(
    output_root: str | Path = "outputs",
    allow_download: bool = True,
    methods: list[str] | None = None,
    jpeg_qualities: list[int] | None = None,
    noise_sigmas: list[float] | None = None,
    scale_factors: list[float] | None = None,
) -> list[dict]:
    config = _load_config()
    image_path = Path(config["dataset"]["image"])
    watermark_path = Path(config["dataset"]["watermark"])
    ensure_demo_data(image_path, watermark_path, allow_download=allow_download)
    image = read_grayscale(image_path)
    watermark_source = read_grayscale(watermark_path)
    output_dir = Path(output_root) / "attacks"
    output_dir.mkdir(parents=True, exist_ok=True)
    selected_methods = methods or config["experiments"]["methods"]
    qualities = jpeg_qualities or config["experiments"]["jpeg_qualities"]
    sigmas = noise_sigmas or config["experiments"]["noise_sigmas"]
    scales = scale_factors or config["experiments"]["scale_factors"]
    rows: list[dict] = []
    for method in selected_methods:
        params = dict(config["methods"][method])
        watermark_size = tuple(params.pop("watermark_size"))
        watermark = prepare_watermark(watermark_source, (int(watermark_size[0]), int(watermark_size[1])))
        watermarker = create_watermarker(method, **params)
        embedded = watermarker.embed(image, watermark)
        attacks = []
        attacks += [("jpeg", q, jpeg_compress(embedded.image, q)) for q in qualities]
        attacks += [("noise", s, gaussian_noise(embedded.image, s)) for s in sigmas]
        attacks += [("resize", s, resize_attack(embedded.image, s)) for s in scales]
        for attack_name, level, attacked in attacks:
            extracted = watermarker.extract(attacked, watermark.shape, original_image=image if method == "dft" else None)
            save_grayscale(output_dir / f"{method}_{attack_name}_{level}_attacked.png", attacked)
            row = {"method": method, "attack": attack_name, "level": level}
            row.update(image_quality(embedded.image, attacked))
            row.update(watermark_quality(watermark, extracted.watermark))
            rows.append(row)
    frame = pd.DataFrame(rows)
    frame.to_csv(output_dir / "metrics_attacks.csv", index=False)
    plot_frame = frame.assign(attack_level=frame["attack"] + "_" + frame["level"].astype(str))
    save_metric_curve(output_dir / "attack_ber.png", plot_frame, x="attack_level", y="ber", hue="method", title="Attack Robustness BER")
    return rows


if __name__ == "__main__":
    run_attacks()
```

- [ ] **Step 4: Run attack experiment tests**

Run: `python -m pytest tests/test_run_attacks.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/run_attacks.py tests/test_run_attacks.py
git commit -m "feat: add robustness attack experiment"
```

---

### Task 14: Run-All Experiment Script

**Files:**
- Create: `experiments/run_all.py`
- Create: `tests/test_run_all.py`

- [ ] **Step 1: Write failing run-all test**

Create `tests/test_run_all.py`:

```python
from experiments.run_all import run_all


def test_run_all_creates_three_metric_files(tmp_path):
    run_all(output_root=tmp_path, allow_download=False, methods=["dft"])
    assert (tmp_path / "basic" / "metrics_basic.csv").exists()
    assert (tmp_path / "strength" / "metrics_strength.csv").exists()
    assert (tmp_path / "attacks" / "metrics_attacks.csv").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_run_all.py -v`

Expected: FAIL because `run_all.py` does not exist.

- [ ] **Step 3: Implement run-all script**

Create `experiments/run_all.py`:

```python
from __future__ import annotations

from pathlib import Path

from experiments.run_attacks import run_attacks
from experiments.run_basic import run_basic
from experiments.run_strength import run_strength


def run_all(output_root: str | Path = "outputs", allow_download: bool = True, methods: list[str] | None = None) -> None:
    run_basic(output_root=output_root, allow_download=allow_download, methods=methods)
    run_strength(output_root=output_root, allow_download=allow_download, methods=methods)
    run_attacks(output_root=output_root, allow_download=allow_download, methods=methods)


if __name__ == "__main__":
    run_all()
```

- [ ] **Step 4: Run run-all tests**

Run: `python -m pytest tests/test_run_all.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/run_all.py tests/test_run_all.py
git commit -m "feat: add one-command experiment runner"
```

---

### Task 15: README and Planning File Updates

**Files:**
- Create: `README.md`
- Modify: `task_plan.md`
- Modify: `progress.md`
- Create: `tests/test_docs.py`

- [ ] **Step 1: Write failing documentation test**

Create `tests/test_docs.py`:

```python
from pathlib import Path


def test_readme_contains_required_submission_sections():
    text = Path("README.md").read_text(encoding="utf-8")
    required = ["快速开始", "算法说明", "进阶实验", "抗攻击能力", "一键运行", "结果输出"]
    for phrase in required:
        assert phrase in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_docs.py -v`

Expected: FAIL because `README.md` does not exist.

- [ ] **Step 3: Write README**

Create `README.md`:

```markdown
# 图像频域水印

本项目实现信号与系统大作业题目5：图像频域水印。系统支持 DFT、DCT、DWT 三种频域水印算法，覆盖基础嵌入/提取、嵌入强度分析和 JPEG 压缩、缩放、加噪等抗攻击能力测试。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python experiments/run_all.py
```

如果公开数据下载失败，程序会生成可运行的示例图像和水印；也可以手动将测试图放入 `data/raw/`，将水印图放入 `data/watermark/`。

## 一键运行

```bash
python experiments/run_basic.py
python experiments/run_strength.py
python experiments/run_attacks.py
python experiments/run_all.py
```

## 命令行演示

```bash
python main.py embed --method dft --image data/raw/lena.png --watermark data/watermark/logo.png --output outputs/demo/dft_watermarked.png
python main.py extract --method dft --image outputs/demo/dft_watermarked.png --original data/raw/lena.png --output outputs/demo/dft_extracted.png
python main.py attack --type jpeg --quality 50 --image outputs/demo/dft_watermarked.png --output outputs/demo/dft_jpeg50.png
```

## 算法说明

- DFT：非盲水印算法，在傅里叶频谱中频区域嵌入水印，提取时需要原始图像。
- DCT：盲水印算法，以 `8x8` 图像块中频 DCT 系数对的大小关系表示水印 bit。
- DWT：小波域水印算法，在 `LH/HL/HH` 子带中嵌入水印，展示多分辨率频域方法。

## 进阶实验

`experiments/run_strength.py` 会扫描不同嵌入强度，输出 PSNR、SSIM、MSE、NC、BER 指标和曲线，用于分析水印强度对图像质量与提取准确率的影响。

## 抗攻击能力

`experiments/run_attacks.py` 会测试 JPEG 压缩、缩放和高斯噪声攻击。攻击后重新提取水印，并统计图像质量与水印恢复质量。

## 结果输出

结果默认保存在 `outputs/`：

- `outputs/basic/`：基础嵌入、提取和对比图。
- `outputs/strength/`：强度实验 CSV 和曲线图。
- `outputs/attacks/`：抗攻击实验 CSV 和对比图。

## 依赖

所有依赖及版本见 `requirements.txt`。
```

- [ ] **Step 4: Update planning files**

Modify `task_plan.md` phase table so Phase 2-7 are marked `complete` after implementation and Phase 8 remains `pending` for report/PPT.

Append to `progress.md`:

```markdown

## 2026-05-19 Implementation
- Implemented modular Python package for DFT, DCT, and DWT watermarking.
- Added CLI and YAML-driven experiment scripts.
- Added metrics, attack simulation, visualization, tests, and README.
- Next: run full experiments, inspect outputs, then prepare report and PPT.
```

- [ ] **Step 5: Run docs test**

Run: `python -m pytest tests/test_docs.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add README.md task_plan.md progress.md tests/test_docs.py
git commit -m "docs: add project usage guide"
```

---

### Task 16: Full Verification

**Files:**
- No new files expected.
- Modify implementation files only if verification reveals a concrete bug.

- [ ] **Step 1: Install dependencies**

Run: `python -m pip install -r requirements.txt`

Expected: all dependencies install successfully.

- [ ] **Step 2: Run full test suite**

Run: `python -m pytest -v`

Expected: all tests PASS.

- [ ] **Step 3: Run basic experiment**

Run: `python experiments/run_basic.py`

Expected: `outputs/basic/metrics_basic.csv`, watermarked images, extracted watermarks, comparison figures, and spectrum figures exist.

- [ ] **Step 4: Run strength experiment**

Run: `python experiments/run_strength.py`

Expected: `outputs/strength/metrics_strength.csv`, `strength_psnr.png`, and `strength_ber.png` exist.

- [ ] **Step 5: Run attack experiment**

Run: `python experiments/run_attacks.py`

Expected: `outputs/attacks/metrics_attacks.csv` and `attack_ber.png` exist.

- [ ] **Step 6: Run CLI smoke commands**

Run:

```bash
python main.py embed --method dct --image data/raw/lena.png --watermark data/watermark/logo.png --output outputs/demo/dct_watermarked.png
python main.py extract --method dct --image outputs/demo/dct_watermarked.png --output outputs/demo/dct_extracted.png
python main.py attack --type jpeg --quality 50 --image outputs/demo/dct_watermarked.png --output outputs/demo/dct_jpeg50.png
```

Expected: all three commands exit successfully and create the requested files.

- [ ] **Step 7: Inspect Git status**

Run: `git status --short`

Expected: no unexpected untracked files except generated `outputs/` and optional local environment files. If `outputs/` should not be committed, add an appropriate `.gitignore` in a new small commit.

- [ ] **Step 8: Final commit for verification fixes**

If fixes were required:

```bash
git add <fixed-files>
git commit -m "fix: stabilize watermarking experiments"
```

If no fixes were required, do not create an empty commit.

---

## Self-Review

- Spec coverage: the plan covers project structure, DFT/DCT/DWT algorithms, CLI, YAML config, demo data, strength experiments, attack experiments, metrics, visualization, tests, README, and planning updates.
- Placeholder scan: no TBD/TODO placeholders remain; every task includes file paths, commands, expected outcomes, and code blocks for implementation steps.
- Type consistency: shared dataclasses are `WatermarkResult` and `ExtractionResult`; each algorithm uses `embed(image, watermark)` and `extract(image, watermark_shape, original_image=None)`; registry names are consistently `dft`, `dct`, and `dwt`.
