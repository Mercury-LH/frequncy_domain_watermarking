from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import yaml

from watermarking.attacks import apply_attack
from watermarking.io_utils import luminance_channel, prepare_watermark, read_color, read_grayscale, replace_luminance, save_grayscale, save_image
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
    display_image = read_color(args.image) if args.color_y else read_grayscale(args.image)
    image = luminance_channel(display_image)
    watermark = read_grayscale(args.watermark)
    shape = tuple(params.pop("watermark_size", watermark.shape))
    prepared = prepare_watermark(watermark, (int(shape[0]), int(shape[1])))
    watermarker = create_watermarker(args.method, **params)
    result = watermarker.embed(image, prepared)
    output_image = replace_luminance(display_image, result.image) if args.color_y else result.image
    save_image(args.output, output_image)
    print(f"Saved watermarked image to {args.output}")


def command_extract(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    params = method_params(config, args.method)
    shape = tuple(params.pop("watermark_size", args.watermark_size))
    display_image = read_color(args.image) if args.color_y else read_grayscale(args.image)
    image = luminance_channel(display_image)
    original = luminance_channel(read_color(args.original)) if args.original and args.color_y else read_grayscale(args.original) if args.original else None
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
    embed.add_argument("--color-y", action="store_true", help="preserve color by embedding in the Y channel")
    embed.set_defaults(func=command_embed, param={})

    extract = subparsers.add_parser("extract")
    extract.add_argument("--method", required=True, choices=list_methods())
    extract.add_argument("--image", required=True)
    extract.add_argument("--original")
    extract.add_argument("--output", required=True)
    extract.add_argument("--watermark-size", nargs=2, type=int, default=(64, 64))
    extract.add_argument("--config", default="configs/experiments.yaml")
    extract.add_argument("--color-y", action="store_true", help="extract from the Y channel of a color image")
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
