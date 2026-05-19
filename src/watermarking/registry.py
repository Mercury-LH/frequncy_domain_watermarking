from __future__ import annotations

from typing import Any

from watermarking.algorithms.base import Watermarker
from watermarking.algorithms.dct import DCTWatermarker
from watermarking.algorithms.dft import DFTWatermarker
from watermarking.algorithms.dwt import DWTWatermarker


_REGISTRY: dict[str, type[Watermarker]] = {
    "dct": DCTWatermarker,
    "dft": DFTWatermarker,
    "dwt": DWTWatermarker,
}


def list_methods() -> list[str]:
    return sorted(_REGISTRY)


def create_watermarker(method: str, **params: Any) -> Watermarker:
    key = method.lower()
    if key not in _REGISTRY:
        available = ", ".join(list_methods())
        raise ValueError(f"Unknown watermarking method '{method}'. Available methods: {available}.")
    return _REGISTRY[key](**params)
