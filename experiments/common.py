from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


def load_config(config_path: str | Path = "configs/experiments.yaml") -> dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def safe_stem(value: str | Path) -> str:
    stem = Path(value).stem if "/" in str(value) or "." in Path(value).name else str(value)
    return re.sub(r"[^A-Za-z0-9_-]+", "_", stem).strip("_") or "image"


def configured_images(config: dict[str, Any]) -> list[dict[str, str]]:
    dataset = config["dataset"]
    images = dataset.get("images")
    if not images:
        image_path = str(dataset["image"])
        return [{"name": safe_stem(image_path), "path": image_path, "source_type": "gray"}]

    normalized: list[dict[str, str]] = []
    for image in images:
        path = str(image["path"])
        name = str(image.get("name") or safe_stem(path))
        normalized.append({"name": safe_stem(name), "path": path, "source_type": str(image.get("source_type", "unknown"))})
    return normalized
