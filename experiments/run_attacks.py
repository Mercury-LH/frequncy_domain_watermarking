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
