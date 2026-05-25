from __future__ import annotations

from pathlib import Path

import pandas as pd

from experiments.common import configured_images, load_config
from watermarking.attacks import gaussian_noise, jpeg_compress, resize_attack
from watermarking.io_utils import ensure_demo_data, luminance_channel, prepare_watermark, read_color, read_grayscale, replace_luminance, save_image
from watermarking.metrics import image_quality, watermark_quality
from watermarking.registry import create_watermarker
from watermarking.visualization import save_metric_curve


def run_attacks(
    output_root: str | Path = "outputs",
    allow_download: bool = True,
    methods: list[str] | None = None,
    jpeg_qualities: list[int] | None = None,
    noise_sigmas: list[float] | None = None,
    scale_factors: list[float] | None = None,
) -> list[dict]:
    config = load_config()
    watermark_path = Path(config["dataset"]["watermark"])
    root_dir = Path(output_root) / "multi_image" / "attacks"
    selected_methods = methods or config["experiments"]["methods"]
    qualities = jpeg_qualities or config["experiments"]["jpeg_qualities"]
    sigmas = noise_sigmas or config["experiments"]["noise_sigmas"]
    scales = scale_factors or config["experiments"]["scale_factors"]
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
            attacks = []
            attacks += [("jpeg", q, jpeg_compress(embedded.image, q)) for q in qualities]
            attacks += [("noise", s, gaussian_noise(embedded.image, s)) for s in sigmas]
            attacks += [("resize", s, resize_attack(embedded.image, s)) for s in scales]
            for attack_name, level, attacked in attacks:
                extracted = watermarker.extract(attacked, watermark.shape, original_image=image if method == "dft" else None)
                save_image(image_dir / f"{method}_{attack_name}_{level}_attacked.png", replace_luminance(display_image, attacked))
                row = {"image_name": image_info["name"], "image_path": str(image_path), "source_type": image_info["source_type"], "processing_channel": "Y" if image_info["source_type"] == "color" else "gray", "method": method, "attack": attack_name, "level": level}
                row.update(image_quality(watermarked_display, replace_luminance(display_image, attacked)))
                row.update(watermark_quality(watermark, extracted.watermark))
                rows.append(row)
                image_rows.append(row)
        image_frame = pd.DataFrame(image_rows)
        image_frame.to_csv(image_dir / "metrics_attacks.csv", index=False)
        image_plot_frame = image_frame.assign(attack_level=image_frame["attack"] + "_" + image_frame["level"].astype(str))
        save_metric_curve(image_dir / "attack_ber.png", image_plot_frame, x="attack_level", y="ber", hue="method", title=f"{image_info['name']} Attack Robustness BER")
    frame = pd.DataFrame(rows)
    frame.to_csv(root_dir / "metrics_attacks_all.csv", index=False)
    plot_frame = frame.assign(attack_level=frame["attack"] + "_" + frame["level"].astype(str))
    save_metric_curve(root_dir / "attack_ber_all.png", plot_frame, x="attack_level", y="ber", hue="method", title="Attack Robustness BER")
    return rows


if __name__ == "__main__":
    run_attacks()
