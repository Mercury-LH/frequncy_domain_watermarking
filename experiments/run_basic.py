from __future__ import annotations

from pathlib import Path

import pandas as pd

from experiments.common import configured_images, load_config
from watermarking.io_utils import ensure_demo_data, luminance_channel, prepare_watermark, read_color, read_grayscale, replace_luminance, save_grayscale, save_image
from watermarking.metrics import image_quality, watermark_quality
from watermarking.registry import create_watermarker
from watermarking.visualization import save_comparison_figure, save_spectrum_figure


def run_basic(output_root: str | Path = "outputs", allow_download: bool = True, methods: list[str] | None = None) -> list[dict]:
    config = load_config()
    watermark_path = Path(config["dataset"]["watermark"])
    selected_methods = methods or config["experiments"]["methods"]
    root_dir = Path(output_root) / "multi_image" / "basic"
    rows: list[dict] = []
    for image_info in configured_images(config):
        image_path = Path(image_info["path"])
        ensure_demo_data(image_path, watermark_path, allow_download=allow_download)
        display_image = read_color(image_path) if image_info["source_type"] == "color" else read_grayscale(image_path)
        image = luminance_channel(display_image)
        watermark_source = read_grayscale(watermark_path)
        image_dir = root_dir / image_info["name"]
        image_dir.mkdir(parents=True, exist_ok=True)
        image_rows: list[dict] = []
        for method in selected_methods:
            params = dict(config["methods"][method])
            watermark_size = tuple(params.pop("watermark_size"))
            watermark = prepare_watermark(watermark_source, (int(watermark_size[0]), int(watermark_size[1])))
            watermarker = create_watermarker(method, **params)
            embedded = watermarker.embed(image, watermark)
            watermarked_display = replace_luminance(display_image, embedded.image)
            original_for_extract = image if method == "dft" else None
            extracted = watermarker.extract(embedded.image, watermark.shape, original_image=original_for_extract)
            watermarked_path = image_dir / f"{method}_watermarked.png"
            extracted_path = image_dir / f"{method}_extracted.png"
            comparison_path = image_dir / f"{method}_comparison.png"
            spectrum_path = image_dir / f"{method}_spectrum.png"
            save_image(watermarked_path, watermarked_display)
            save_grayscale(extracted_path, extracted.watermark)
            save_comparison_figure(comparison_path, display_image, watermarked_display, watermark, extracted.watermark, title=f"{image_info['name']} {method.upper()} Basic Result")
            save_spectrum_figure(spectrum_path, embedded.image)
            row = {"image_name": image_info["name"], "image_path": str(image_path), "source_type": image_info["source_type"], "processing_channel": "Y" if image_info["source_type"] == "color" else "gray", "method": method}
            row.update(image_quality(display_image, watermarked_display))
            row.update(watermark_quality(watermark, extracted.watermark))
            rows.append(row)
            image_rows.append(row)
        pd.DataFrame(image_rows).to_csv(image_dir / "metrics_basic.csv", index=False)
    pd.DataFrame(rows).to_csv(root_dir / "metrics_basic_all.csv", index=False)
    return rows


if __name__ == "__main__":
    run_basic()
