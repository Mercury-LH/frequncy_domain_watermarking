from __future__ import annotations

from pathlib import Path

import pandas as pd

from experiments.common import configured_images, load_config
from watermarking.io_utils import ensure_demo_data, luminance_channel, prepare_watermark, read_color, read_grayscale, replace_luminance
from watermarking.metrics import image_quality, watermark_quality
from watermarking.registry import create_watermarker
from watermarking.visualization import save_metric_curve


def _strength_key(method: str) -> str:
    return "delta" if method == "dct" else "alpha"


def run_strength(output_root: str | Path = "outputs", allow_download: bool = True, methods: list[str] | None = None, strengths: dict[str, list[float]] | None = None) -> list[dict]:
    config = load_config()
    watermark_path = Path(config["dataset"]["watermark"])
    root_dir = Path(output_root) / "multi_image" / "strength"
    selected_methods = methods or config["experiments"]["methods"]
    sweep = strengths or config["experiments"]["strengths"]
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
            for value in sweep[method]:
                params = dict(config["methods"][method])
                watermark_size = tuple(params.pop("watermark_size"))
                params[_strength_key(method)] = value
                watermark = prepare_watermark(watermark_source, (int(watermark_size[0]), int(watermark_size[1])))
                watermarker = create_watermarker(method, **params)
                embedded = watermarker.embed(image, watermark)
                watermarked_display = replace_luminance(display_image, embedded.image)
                extracted = watermarker.extract(embedded.image, watermark.shape, original_image=image if method == "dft" else None)
                row = {"image_name": image_info["name"], "image_path": str(image_path), "source_type": image_info["source_type"], "processing_channel": "Y" if image_info["source_type"] == "color" else "gray", "method": method, "strength": value}
                row.update(image_quality(display_image, watermarked_display))
                row.update(watermark_quality(watermark, extracted.watermark))
                rows.append(row)
                image_rows.append(row)
        image_frame = pd.DataFrame(image_rows)
        image_frame.to_csv(image_dir / "metrics_strength.csv", index=False)
        save_metric_curve(image_dir / "strength_psnr.png", image_frame, x="strength", y="psnr", hue="method", title=f"{image_info['name']} Strength vs PSNR")
        save_metric_curve(image_dir / "strength_ber.png", image_frame, x="strength", y="ber", hue="method", title=f"{image_info['name']} Strength vs BER")
    frame = pd.DataFrame(rows)
    frame.to_csv(root_dir / "metrics_strength_all.csv", index=False)
    save_metric_curve(root_dir / "strength_psnr_all.png", frame, x="strength", y="psnr", hue="method", title="Embedding Strength vs PSNR")
    save_metric_curve(root_dir / "strength_ber_all.png", frame, x="strength", y="ber", hue="method", title="Embedding Strength vs BER")
    return rows


if __name__ == "__main__":
    run_strength()
