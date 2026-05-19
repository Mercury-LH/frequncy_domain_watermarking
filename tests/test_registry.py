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
