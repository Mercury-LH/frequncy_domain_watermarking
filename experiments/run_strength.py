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
