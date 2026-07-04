from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
for p in (str(REPO_ROOT), str(REPO_ROOT / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

import cv2
import numpy as np

from watermarking.io_utils import create_synthetic_image, read_color
from webapp.backend import services

STORY_DIR = REPO_ROOT / "webapp" / "frontend" / "public" / "story"
SAMPLES_DIR = REPO_ROOT / "webapp" / "frontend" / "public" / "samples"
CANDIDATES = sorted((REPO_ROOT / "data" / "images" / "test").glob("*.jpg")) + sorted((REPO_ROOT / "data" / "misc").glob("*.tiff"))


def _load_host() -> np.ndarray:
    for path in CANDIDATES:
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is not None and min(image.shape[:2]) >= 256:
            return services.downscale(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    return cv2.cvtColor(create_synthetic_image((512, 512)), cv2.COLOR_GRAY2RGB)


def _save(name: str, b64: str) -> None:
    (STORY_DIR / name).write_bytes(base64.b64decode(b64))


def main() -> None:
    STORY_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    host = _load_host()
    watermark = services.render_text_watermark("隐形水印")
    embed = services.run_embed(host, watermark, "dct", 12.0)

    _save("01-photo.png", services.png_b64(host))
    _save("02-spectrum.png", embed["spectrum_before_b64"])
    _save("03-spectrum-marked.png", embed["spectrum_after_b64"])
    _save("04-watermarked.png", embed["watermarked_png_b64"])

    watermarked = services.decode_host_image(base64.b64decode(embed["watermarked_png_b64"]))
    diff = np.clip(np.abs(watermarked.astype(np.int16) - host.astype(np.int16)) * 20, 0, 255).astype(np.uint8)
    _save("04-diff20.png", services.png_b64(diff))

    side = embed["params"]["wm_w"]
    outcome = services.run_attack(watermarked, "jpeg", 90, "dct", side, side)
    _save("05-attacked.png", outcome["attacked_png_b64"])
    _save("06-extracted.png", outcome["extracted_png_b64"])

    (STORY_DIR / "story.json").write_text(
        json.dumps({"psnr": embed["metrics"]["psnr"], "ssim": embed["metrics"]["ssim"], "nc": outcome["watermark"]["nc"]})
    )

    for index, path in enumerate(CANDIDATES[:2], start=1):
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is not None:
            cv2.imwrite(str(SAMPLES_DIR / f"sample{index}.jpg"), services.downscale(image))

    print(f"story assets -> {STORY_DIR}")
    print(f"samples -> {SAMPLES_DIR}")


if __name__ == "__main__":
    main()
