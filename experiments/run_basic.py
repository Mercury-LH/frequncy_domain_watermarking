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
