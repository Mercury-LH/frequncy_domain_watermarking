# 隐形水印工坊 Web 应用 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把本仓库的 DFT/DCT/DWT 频域水印算法转化为免费上线的双语 Web 应用（滚动叙事 + 嵌入/提取/攻击工具区），部署到 Hugging Face Spaces。

**Architecture:** FastAPI 后端直接 import 现有 `src/watermarking/` 模块（零改动），无状态内存处理；React (Vite+TS+Tailwind v4) 前端构建为静态文件由 FastAPI 一起服务；单 Docker 镜像部署。叙事演示帧离线预生成并提交进仓库。

**Tech Stack:** FastAPI 0.111 / Pillow / slowapi；React 18 + Vite 5 + TypeScript + Tailwind v4 + GSAP ScrollTrigger + vitest；Docker (python:3.11-slim + node:20 构建阶段)；Hugging Face Spaces (Docker SDK, 端口 7860)。

**设计依据:** `docs/superpowers/specs/2026-07-04-watermark-webapp-design.md`、根目录 `PRODUCT.md`（brand register）与 `DESIGN.md`（OKLCH tokens、字体、禁令清单）。

## Global Constraints

- 现有 `src/watermarking/`、`experiments/`、`tests/` 一律不修改。
- 后端无状态：不写磁盘、无数据库；图片 multipart 进、base64 JSON 出。
- 上传 ≤ 10MB；处理前最长边缩至 1024px（输出即该尺寸，界面明示）；图片最短边 ≥ 128px；水印文字 ≤ 20 字符。
- 所有面向用户的文案必须同时存在于 zh/en 两份字典（vitest 有键完整性测试）；后端错误返回 `{"error": {"code", "zh", "en"}}`。
- 提取水印时必须**新建** Watermarker 实例——`DWTWatermarker.extract` 会走 `_last_watermark` 同实例缓存，复用嵌入实例会产生假结果。
- 强度参数范围（前端滑杆与后端校验一致，Task 5 校准后）：dct `delta∈[4,24]` 默认 12；dft `alpha∈[2,20]` 默认 **3**（原 10 使 PSNR 跌破 30dB）；dwt `alpha∈[0.01,0.5]` 默认 0.05。
- DWT 定位为**嵌入演示**：其盲提取（中值阈值）对稀疏水印结构性失效（实测 NC≈0.05），往返保真只由 DCT/DFT 承诺；界面文案如实标注。
- PSNR 可能为 `inf`，序列化前用 `min(psnr, 99.0)` 截断。
- 视觉遵循 `DESIGN.md`：OKLCH tokens、禁渐变文字/玻璃拟态/侧边彩条/eyebrow 标签/奶油底色；动效 150–250ms 指数缓出；`prefers-reduced-motion` 全适配；WCAG AA 对比度。
- 端口：本地后端 8000，前端 dev 5173（proxy /api → 8000）；Docker/HF 7860。
- 请求超时：前端 fetch 45 秒 AbortSignal 兜底（单张图处理为毫秒级，spec 的"30 秒上限"由此覆盖，不在服务端另设机制）。
- 提交信息用英文 conventional commits（feat:/test:/chore:）。

## 文件地图

```
webapp/
├── backend/
│   ├── __init__.py            # 空文件（包标记）
│   ├── app.py                 # FastAPI 工厂、异常处理、静态文件服务
│   ├── routes.py              # /api/embed /api/extract /api/attack /api/health
│   ├── services.py            # 校验、文字水印渲染、频谱图、PNG 元数据、三条处理管线
│   ├── errors.py              # ApiError + 双语错误目录
│   ├── requirements.txt       # 生产依赖（Docker 用，含 opencv-python-headless）
│   └── tests/
│       ├── conftest.py        # sys.path 注入 + 共享 fixtures
│       ├── test_health.py
│       ├── test_services.py
│       ├── test_embed_api.py
│       ├── test_extract_api.py
│       ├── test_attack_api.py
│       └── test_limits.py
├── frontend/
│   ├── index.html / package.json / vite.config.ts / tsconfig.json
│   ├── public/story/          # 预生成叙事帧 + story.json（Task 15 产出，提交进仓库）
│   ├── public/samples/        # 示例图（Task 15 产出）
│   └── src/
│       ├── main.tsx / App.tsx
│       ├── styles/tokens.css                    # DESIGN.md 的 OKLCH tokens
│       ├── i18n/{zh.ts, en.ts, index.tsx}
│       ├── lib/{api.ts, pngMeta.ts}
│       ├── state/workbench.tsx                  # 跨标签页共享嵌入结果
│       ├── components/{LangToggle, Dropzone, MethodPicker, StrengthSlider,
│       │               MetricRow, ResultImage, ColdStartGate}.tsx
│       └── sections/
│           ├── Hero.tsx / Story.tsx / StoryStatic.tsx / CtaBridge.tsx / Footer.tsx
│           └── workbench/{Workbench, EmbedTab, ExtractTab, AttackTab}.tsx
├── scripts/gen_story_assets.py                  # 离线生成叙事帧与示例图
Dockerfile / .dockerignore
.github/workflows/deploy.yml
```

**任务顺序**：Task 1–6 后端（每个独立可测）→ Task 7–13 前端工具区 → Task 14–15 叙事 → Task 16–18 部署与终检。

---

### Task 1: 后端骨架 + /api/health

**Files:**
- Create: `webapp/backend/__init__.py`（空）
- Create: `webapp/backend/errors.py`
- Create: `webapp/backend/app.py`
- Create: `webapp/backend/routes.py`
- Create: `webapp/backend/requirements.txt`
- Create: `webapp/backend/tests/conftest.py`
- Test: `webapp/backend/tests/test_health.py`

**Interfaces:**
- Produces: `create_app() -> FastAPI`（app.py）；`ApiError(status:int, code:str, zh:str, en:str)` 异常类型（errors.py）；`router: APIRouter`（routes.py，前缀 /api 由 app.py 挂载）；tests fixture `client: TestClient`。

- [ ] **Step 1: 安装本地开发依赖**（复用研究项目 .venv，已有 numpy/opencv/skimage/pywt）

```bash
source .venv/bin/activate 2>/dev/null || python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
pip install fastapi==0.111.0 "uvicorn[standard]==0.30.1" python-multipart==0.0.9 slowapi==0.1.9 Pillow==10.3.0 httpx==0.27.0
```

- [ ] **Step 2: 写失败测试** `webapp/backend/tests/conftest.py`：

```python
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
for p in (str(REPO_ROOT), str(REPO_ROOT / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
import pytest
from fastapi.testclient import TestClient

from watermarking.io_utils import create_synthetic_image, create_synthetic_watermark
from webapp.backend.app import create_app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


@pytest.fixture()
def synthetic_image() -> np.ndarray:
    return create_synthetic_image((512, 512))


@pytest.fixture()
def synthetic_watermark() -> np.ndarray:
    return create_synthetic_watermark((64, 64))


def encode_png(array: np.ndarray) -> bytes:
    import cv2

    ok, buf = cv2.imencode(".png", array)
    assert ok
    return buf.tobytes()
```

`webapp/backend/tests/test_health.py`：

```python
def test_health_returns_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 3: 跑测试确认失败**

Run: `pytest webapp/backend/tests/test_health.py -v`
Expected: FAIL（`ModuleNotFoundError: webapp.backend.app`）

- [ ] **Step 4: 最小实现**

`webapp/backend/__init__.py`：空文件。`webapp/backend/tests/__init__.py` 不需要。

`webapp/backend/errors.py`：

```python
from __future__ import annotations


class ApiError(Exception):
    def __init__(self, status: int, code: str, zh: str, en: str) -> None:
        super().__init__(code)
        self.status = status
        self.code = code
        self.zh = zh
        self.en = en

    def payload(self) -> dict:
        return {"error": {"code": self.code, "zh": self.zh, "en": self.en}}


def file_too_large() -> ApiError:
    return ApiError(413, "file_too_large", "文件超过 10MB 上限", "File exceeds the 10MB limit")


def unsupported_format() -> ApiError:
    return ApiError(400, "unsupported_format", "无法识别的图片格式（支持 JPG/PNG/WebP/TIFF）", "Unrecognized image format (JPG/PNG/WebP/TIFF supported)")


def image_too_small() -> ApiError:
    return ApiError(400, "image_too_small", "图片太小：最短边需 ≥ 128 像素", "Image too small: shortest side must be ≥ 128px")


def text_too_long() -> ApiError:
    return ApiError(400, "text_too_long", "水印文字最长 20 个字符", "Watermark text is limited to 20 characters")


def missing_watermark() -> ApiError:
    return ApiError(400, "missing_watermark", "请提供水印文字或水印图片", "Provide watermark text or a watermark image")


def dft_requires_original() -> ApiError:
    return ApiError(422, "dft_requires_original", "DFT 是非盲算法，提取时需要上传原图", "DFT is non-blind: extraction requires the original image")


def bad_strength(method: str, low: float, high: float) -> ApiError:
    return ApiError(400, "bad_strength", f"{method.upper()} 强度需在 {low}–{high} 之间", f"{method.upper()} strength must be within {low}–{high}")


def bad_method() -> ApiError:
    return ApiError(400, "bad_method", "算法必须是 dft / dct / dwt 之一", "Method must be one of dft / dct / dwt")


def bad_attack() -> ApiError:
    return ApiError(400, "bad_attack", "攻击类型必须是 jpeg / resize / noise 之一", "Attack must be one of jpeg / resize / noise")


def shape_mismatch() -> ApiError:
    return ApiError(422, "shape_mismatch", "原图与含水印图尺寸不一致", "Original and watermarked images differ in size")
```

`webapp/backend/routes.py`：

```python
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}
```

`webapp/backend/app.py`：

```python
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(REPO_ROOT), str(REPO_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from webapp.backend.errors import ApiError
from webapp.backend.routes import router

FRONTEND_DIST = REPO_ROOT / "webapp" / "frontend" / "dist"


def create_app() -> FastAPI:
    app = FastAPI(title="Invisible Watermark Studio", docs_url=None, redoc_url=None)

    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(status_code=exc.status, content=exc.payload())

    app.include_router(router, prefix="/api")

    if FRONTEND_DIST.is_dir():
        app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
    return app


app = create_app()
```

`webapp/backend/requirements.txt`（Docker 生产依赖）：

```
fastapi==0.111.0
uvicorn[standard]==0.30.1
python-multipart==0.0.9
slowapi==0.1.9
Pillow==10.3.0
numpy==1.26.4
opencv-python-headless==4.9.0.80
scipy==1.12.0
scikit-image==0.22.0
PyWavelets==1.5.0
```

- [ ] **Step 5: 跑测试确认通过**

Run: `pytest webapp/backend/tests/test_health.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add webapp/backend
git commit -m "feat: scaffold FastAPI backend with health endpoint"
```

---

### Task 2: services——上传解码、校验、缩放

**Files:**
- Create: `webapp/backend/services.py`
- Test: `webapp/backend/tests/test_services.py`

**Interfaces:**
- Consumes: `errors.py` 的工厂函数。
- Produces: `MAX_BYTES = 10 * 1024 * 1024`；`decode_host_image(data: bytes) -> np.ndarray`（RGB uint8，已缩放，最短边校验）；`decode_watermark_image(data: bytes) -> np.ndarray`（灰度 uint8）；`downscale(image: np.ndarray, max_side: int = 1024) -> np.ndarray`。

- [ ] **Step 1: 写失败测试**（追加到 `webapp/backend/tests/test_services.py`）

```python
from __future__ import annotations

import numpy as np
import pytest

from webapp.backend import services
from webapp.backend.errors import ApiError
from webapp.backend.tests.conftest import encode_png


def test_decode_host_image_returns_rgb(synthetic_image):
    data = encode_png(synthetic_image)
    decoded = services.decode_host_image(data)
    assert decoded.ndim == 3 and decoded.shape[2] == 3
    assert decoded.dtype == np.uint8


def test_decode_host_image_downscales_long_side():
    big = np.random.default_rng(0).integers(0, 255, (300, 2048), dtype=np.uint8)
    decoded = services.decode_host_image(encode_png(big))
    assert max(decoded.shape[:2]) == 1024


def test_decode_host_image_rejects_garbage():
    with pytest.raises(ApiError) as excinfo:
        services.decode_host_image(b"not an image at all")
    assert excinfo.value.code == "unsupported_format"


def test_decode_host_image_rejects_oversize():
    with pytest.raises(ApiError) as excinfo:
        services.decode_host_image(b"\x00" * (services.MAX_BYTES + 1))
    assert excinfo.value.code == "file_too_large"


def test_decode_host_image_rejects_tiny():
    tiny = np.zeros((64, 64), dtype=np.uint8)
    with pytest.raises(ApiError) as excinfo:
        services.decode_host_image(encode_png(tiny))
    assert excinfo.value.code == "image_too_small"


def test_decode_watermark_image_is_grayscale(synthetic_watermark):
    decoded = services.decode_watermark_image(encode_png(synthetic_watermark))
    assert decoded.ndim == 2
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pytest webapp/backend/tests/test_services.py -v`
Expected: FAIL（`services` 无属性）

- [ ] **Step 3: 实现** `webapp/backend/services.py`：

```python
from __future__ import annotations

import cv2
import numpy as np

from webapp.backend import errors

MAX_BYTES = 10 * 1024 * 1024
MAX_SIDE = 1024
MIN_SIDE = 128


def downscale(image: np.ndarray, max_side: int = MAX_SIDE) -> np.ndarray:
    height, width = image.shape[:2]
    longest = max(height, width)
    if longest <= max_side:
        return image
    scale = max_side / longest
    return cv2.resize(image, (max(1, round(width * scale)), max(1, round(height * scale))), interpolation=cv2.INTER_AREA)


def _decode(data: bytes, flags: int) -> np.ndarray:
    if len(data) > MAX_BYTES:
        raise errors.file_too_large()
    array = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), flags)
    if array is None:
        raise errors.unsupported_format()
    return array


def decode_host_image(data: bytes) -> np.ndarray:
    bgr = _decode(data, cv2.IMREAD_COLOR)
    if min(bgr.shape[:2]) < MIN_SIDE:
        raise errors.image_too_small()
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return downscale(rgb)


def decode_watermark_image(data: bytes) -> np.ndarray:
    gray = _decode(data, cv2.IMREAD_GRAYSCALE)
    return downscale(gray, 512)
```

- [ ] **Step 4: 跑测试确认通过**

Run: `pytest webapp/backend/tests/test_services.py -v`
Expected: PASS（6 个测试）

- [ ] **Step 5: Commit**

```bash
git add webapp/backend/services.py webapp/backend/tests/test_services.py
git commit -m "feat: add upload decoding and validation services"
```

---

### Task 3: services——文字水印渲染（支持中文）

**Files:**
- Modify: `webapp/backend/services.py`（追加）
- Modify: `webapp/backend/tests/test_services.py`（追加）

**Interfaces:**
- Produces: `find_cjk_font() -> str`（环境变量 `WATERMARK_FONT` 可覆盖）；`render_text_watermark(text: str, canvas: int = 256) -> np.ndarray`（二值 uint8 0/255，正方形）。

- [ ] **Step 1: 追加失败测试**

```python
def test_render_text_watermark_chinese_not_blank():
    bitmap = services.render_text_watermark("水印测试")
    assert bitmap.shape == (256, 256)
    assert set(np.unique(bitmap)).issubset({0, 255})
    assert (bitmap == 255).mean() > 0.01


def test_render_text_watermark_differs_by_text():
    a = services.render_text_watermark("ABC")
    b = services.render_text_watermark("XYZ")
    assert (a != b).any()


def test_render_text_watermark_rejects_long_text():
    with pytest.raises(ApiError) as excinfo:
        services.render_text_watermark("字" * 21)
    assert excinfo.value.code == "text_too_long"


def test_render_text_watermark_rejects_empty():
    with pytest.raises(ApiError) as excinfo:
        services.render_text_watermark("   ")
    assert excinfo.value.code == "missing_watermark"
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pytest webapp/backend/tests/test_services.py -k text_watermark -v`
Expected: FAIL

- [ ] **Step 3: 实现**（追加到 services.py；顶部补 `import os` 与 `from PIL import Image, ImageDraw, ImageFont`）

```python
_FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "C:/Windows/Fonts/msyh.ttc",
]


def find_cjk_font() -> str:
    override = os.environ.get("WATERMARK_FONT")
    candidates = [override] + _FONT_CANDIDATES if override else _FONT_CANDIDATES
    for path in candidates:
        if path and os.path.exists(path):
            return path
    raise RuntimeError("No CJK-capable font found; set WATERMARK_FONT to a .ttf/.ttc path.")


def render_text_watermark(text: str, canvas: int = 256) -> np.ndarray:
    cleaned = text.strip()
    if not cleaned:
        raise errors.missing_watermark()
    if len(cleaned) > 20:
        raise errors.text_too_long()
    font_path = find_cjk_font()
    image = Image.new("L", (canvas, canvas), 0)
    draw = ImageDraw.Draw(image)
    size = canvas
    while size > 8:
        font = ImageFont.truetype(font_path, size)
        left, top, right, bottom = draw.textbbox((0, 0), cleaned, font=font)
        if right - left <= canvas - 16 and bottom - top <= canvas - 16:
            break
        size = int(size * 0.85)
    x = (canvas - (right - left)) // 2 - left
    y = (canvas - (bottom - top)) // 2 - top
    draw.text((x, y), cleaned, fill=255, font=font)
    array = np.array(image, dtype=np.uint8)
    return np.where(array > 127, 255, 0).astype(np.uint8)
```

- [ ] **Step 4: 跑测试确认通过**

Run: `pytest webapp/backend/tests/test_services.py -v`
Expected: PASS（10 个测试）

- [ ] **Step 5: Commit**

```bash
git add webapp/backend/services.py webapp/backend/tests/test_services.py
git commit -m "feat: render text watermarks with CJK font support"
```

---

### Task 4: services——频谱图与 PNG 参数元数据

**Files:**
- Modify: `webapp/backend/services.py`（追加）
- Modify: `webapp/backend/tests/test_services.py`（追加）

**Interfaces:**
- Produces: `spectrum_png_b64(gray: np.ndarray) -> str`；`png_b64(image: np.ndarray) -> str`（灰度或 RGB → base64 PNG）；`png_bytes_with_params(image_rgb: np.ndarray, params: dict) -> bytes`（写 tEXt 关键字 `watermark-params`，值为 JSON）；`read_png_params(data: bytes) -> dict | None`。
- 参数 JSON 结构（前后端契约，v1）：`{"v": 1, "method": "dct", "strength": 12.0, "wm_w": 64, "wm_h": 64}`。

- [ ] **Step 1: 追加失败测试**

```python
def test_spectrum_png_b64_decodes(synthetic_image):
    import base64

    b64 = services.spectrum_png_b64(synthetic_image.astype(np.float64))
    raw = base64.b64decode(b64)
    assert raw[:8] == b"\x89PNG\r\n\x1a\n"


def test_png_params_roundtrip(synthetic_image):
    import cv2

    rgb = cv2.cvtColor(synthetic_image, cv2.COLOR_GRAY2RGB)
    params = {"v": 1, "method": "dct", "strength": 12.0, "wm_w": 64, "wm_h": 64}
    data = services.png_bytes_with_params(rgb, params)
    assert services.read_png_params(data) == params


def test_read_png_params_none_when_absent(synthetic_image):
    assert services.read_png_params(encode_png(synthetic_image)) is None
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pytest webapp/backend/tests/test_services.py -k "spectrum or png_params" -v`
Expected: FAIL

- [ ] **Step 3: 实现**（追加到 services.py；顶部补 `import base64, io, json` 与 `from PIL.PngImagePlugin import PngInfo`）

```python
PARAMS_KEYWORD = "watermark-params"


def png_b64(image: np.ndarray) -> str:
    if image.ndim == 3:
        encoded = cv2.imencode(".png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))[1]
    else:
        encoded = cv2.imencode(".png", image)[1]
    return base64.b64encode(encoded.tobytes()).decode("ascii")


def spectrum_png_b64(gray: np.ndarray) -> str:
    spectrum = np.fft.fftshift(np.fft.fft2(gray.astype(np.float64)))
    magnitude = np.log1p(np.abs(spectrum))
    lo, hi = float(magnitude.min()), float(magnitude.max())
    normalized = np.zeros_like(magnitude) if hi <= lo else (magnitude - lo) / (hi - lo)
    return png_b64((normalized * 255).astype(np.uint8))


def png_bytes_with_params(image_rgb: np.ndarray, params: dict) -> bytes:
    info = PngInfo()
    info.add_text(PARAMS_KEYWORD, json.dumps(params))
    buffer = io.BytesIO()
    Image.fromarray(image_rgb).save(buffer, format="PNG", pnginfo=info)
    return buffer.getvalue()


def read_png_params(data: bytes) -> dict | None:
    try:
        text = Image.open(io.BytesIO(data)).text.get(PARAMS_KEYWORD)
    except Exception:
        return None
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
```

- [ ] **Step 4: 跑测试确认通过**

Run: `pytest webapp/backend/tests/test_services.py -v`
Expected: PASS（13 个测试）

- [ ] **Step 5: Commit**

```bash
git add webapp/backend/services.py webapp/backend/tests/test_services.py
git commit -m "feat: add spectrum rendering and PNG params metadata"
```

---

### Task 5: services——嵌入/提取/攻击三条管线

**Files:**
- Modify: `webapp/backend/services.py`（追加）
- Modify: `webapp/backend/tests/test_services.py`（追加）

**Interfaces:**
- Consumes: `watermarking.registry.create_watermarker`、`watermarking.io_utils.{luminance_channel, replace_luminance, prepare_watermark}`、`watermarking.metrics.{image_quality, watermark_quality}`、`watermarking.attacks.apply_attack`。
- Produces:
  - `STRENGTH_RANGES: dict[str, tuple[float, float, float]]`（method → (low, high, default)）
  - `choose_watermark_side(height: int, width: int) -> int`
  - `run_embed(host_rgb, watermark_gray, method: str, strength: float) -> dict`，返回键：`watermarked_png_b64, metrics{psnr,ssim}, spectrum_before_b64, spectrum_after_b64, params{v,method,strength,wm_w,wm_h}, prepared_watermark_png_b64`
  - `run_extract(image_rgb, method, wm_w, wm_h, original_rgb=None, reference_watermark=None) -> dict`，返回键：`watermark_png_b64` 及可选 `nc, ber`
  - `attack_image(image_rgb, attack: str, param: float) -> np.ndarray`（彩色感知版 jpeg/resize/noise）
  - `run_attack(image_rgb, attack, param, method, wm_w, wm_h, original_rgb=None) -> dict`，返回键：`attacked_png_b64, extracted_png_b64, metrics{psnr,ssim}, watermark{nc,ber}`（nc/ber 为攻击后提取 vs 攻击前提取的对比）

- [ ] **Step 1: 追加失败测试**

```python
def test_choose_watermark_side_512():
    assert services.choose_watermark_side(512, 512) == 64


def test_choose_watermark_side_small_image():
    assert services.choose_watermark_side(256, 256) == 32


def test_strength_validation():
    with pytest.raises(ApiError) as excinfo:
        services.validate_strength("dct", 100.0)
    assert excinfo.value.code == "bad_strength"


@pytest.mark.parametrize("method", ["dct", "dft", "dwt"])
def test_embed_extract_roundtrip(method, synthetic_image, synthetic_watermark):
    import cv2

    rgb = cv2.cvtColor(synthetic_image, cv2.COLOR_GRAY2RGB)
    result = services.run_embed(rgb, synthetic_watermark, method, services.STRENGTH_RANGES[method][2])
    assert result["metrics"]["psnr"] > 30.0
    params = result["params"]
    watermarked = services.decode_host_image(__import__("base64").b64decode(result["watermarked_png_b64"]))
    original = rgb if method == "dft" else None
    extraction = services.run_extract(
        watermarked, method, params["wm_w"], params["wm_h"],
        original_rgb=original, reference_watermark=synthetic_watermark,
    )
    assert extraction["nc"] > 0.85


def test_run_extract_dft_without_original_raises(synthetic_image):
    import cv2

    rgb = cv2.cvtColor(synthetic_image, cv2.COLOR_GRAY2RGB)
    with pytest.raises(ApiError) as excinfo:
        services.run_extract(rgb, "dft", 64, 64)
    assert excinfo.value.code == "dft_requires_original"


def test_attack_image_jpeg_keeps_shape(synthetic_image):
    import cv2

    rgb = cv2.cvtColor(synthetic_image, cv2.COLOR_GRAY2RGB)
    attacked = services.attack_image(rgb, "jpeg", 60)
    assert attacked.shape == rgb.shape


def test_run_attack_dct_survives_mild_jpeg(synthetic_image, synthetic_watermark):
    import base64

    import cv2

    rgb = cv2.cvtColor(synthetic_image, cv2.COLOR_GRAY2RGB)
    embed = services.run_embed(rgb, synthetic_watermark, "dct", 12.0)
    watermarked = services.decode_host_image(base64.b64decode(embed["watermarked_png_b64"]))
    outcome = services.run_attack(watermarked, "jpeg", 90, "dct", 64, 64)
    assert outcome["watermark"]["nc"] > 0.5
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pytest webapp/backend/tests/test_services.py -k "roundtrip or side or strength or attack" -v`
Expected: FAIL

- [ ] **Step 3: 实现**（追加到 services.py；顶部补 `import math` 与下列导入）

```python
from watermarking.attacks import apply_attack
from watermarking.io_utils import luminance_channel, prepare_watermark, replace_luminance
from watermarking.metrics import image_quality, watermark_quality
from watermarking.registry import create_watermarker

STRENGTH_RANGES: dict[str, tuple[float, float, float]] = {
    "dct": (4.0, 24.0, 12.0),
    "dft": (2.0, 20.0, 10.0),
    "dwt": (0.01, 0.5, 0.05),
}
_STRENGTH_PARAM = {"dct": "delta", "dft": "alpha", "dwt": "alpha"}


def validate_method(method: str) -> str:
    key = method.lower()
    if key not in STRENGTH_RANGES:
        raise errors.bad_method()
    return key


def validate_strength(method: str, strength: float) -> float:
    low, high, _ = STRENGTH_RANGES[validate_method(method)]
    if not low <= strength <= high:
        raise errors.bad_strength(method, low, high)
    return float(strength)


def choose_watermark_side(height: int, width: int) -> int:
    side = min(64, int(math.sqrt((height // 8) * (width // 8))))
    if side < 8:
        raise errors.image_too_small()
    return side


def _make(method: str, strength: float):
    return create_watermarker(method, **{_STRENGTH_PARAM[method]: strength})


def _capped_quality(reference: np.ndarray, candidate: np.ndarray) -> dict:
    quality = image_quality(reference, candidate)
    return {"psnr": round(min(quality["psnr"], 99.0), 2), "ssim": round(quality["ssim"], 4)}


def run_embed(host_rgb: np.ndarray, watermark_gray: np.ndarray, method: str, strength: float) -> dict:
    method = validate_method(method)
    strength = validate_strength(method, strength)
    height, width = host_rgb.shape[:2]
    side = choose_watermark_side(height, width)
    prepared = prepare_watermark(watermark_gray, (side, side))
    luminance = luminance_channel(host_rgb)
    result = _make(method, strength).embed(luminance, prepared)
    output_rgb = replace_luminance(host_rgb, result.image)
    params = {"v": 1, "method": method, "strength": strength, "wm_w": side, "wm_h": side}
    return {
        "watermarked_png_b64": base64.b64encode(png_bytes_with_params(output_rgb, params)).decode("ascii"),
        "metrics": _capped_quality(host_rgb, output_rgb),
        "spectrum_before_b64": spectrum_png_b64(luminance),
        "spectrum_after_b64": spectrum_png_b64(result.image),
        "params": params,
        "prepared_watermark_png_b64": png_b64(prepared),
    }


def run_extract(
    image_rgb: np.ndarray,
    method: str,
    wm_w: int,
    wm_h: int,
    original_rgb: np.ndarray | None = None,
    reference_watermark: np.ndarray | None = None,
) -> dict:
    method = validate_method(method)
    if method == "dft" and original_rgb is None:
        raise errors.dft_requires_original()
    luminance = luminance_channel(image_rgb)
    original = luminance_channel(original_rgb) if original_rgb is not None else None
    if original is not None and original.shape != luminance.shape:
        raise errors.shape_mismatch()
    low, high, default = STRENGTH_RANGES[method]
    extraction = _make(method, default).extract(luminance, (int(wm_h), int(wm_w)), original_image=original)
    payload: dict = {"watermark_png_b64": png_b64(extraction.watermark)}
    if reference_watermark is not None:
        reference = prepare_watermark(reference_watermark, (int(wm_h), int(wm_w)))
        quality = watermark_quality(reference, extraction.watermark)
        payload["nc"] = round(quality["nc"], 4)
        payload["ber"] = round(quality["ber"], 4)
    return payload


_ATTACKS = {"jpeg", "resize", "noise"}


def attack_image(image_rgb: np.ndarray, attack: str, param: float) -> np.ndarray:
    key = attack.lower()
    if key not in _ATTACKS:
        raise errors.bad_attack()
    if key == "jpeg":
        quality = int(np.clip(param, 1, 100))
        bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        ok, encoded = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if not ok:
            raise errors.unsupported_format()
        return cv2.cvtColor(cv2.imdecode(encoded, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    if key == "resize":
        scale = float(np.clip(param, 0.1, 1.0))
        height, width = image_rgb.shape[:2]
        small = cv2.resize(image_rgb, (max(1, int(width * scale)), max(1, int(height * scale))), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(small, (width, height), interpolation=cv2.INTER_LINEAR)
    sigma = float(np.clip(param, 0.0, 50.0))
    noise = np.random.default_rng(42).normal(0, sigma, size=image_rgb.shape)
    return np.clip(image_rgb.astype(np.float64) + noise, 0, 255).astype(np.uint8)


def run_attack(
    image_rgb: np.ndarray,
    attack: str,
    param: float,
    method: str,
    wm_w: int,
    wm_h: int,
    original_rgb: np.ndarray | None = None,
) -> dict:
    method = validate_method(method)
    before = run_extract(image_rgb, method, wm_w, wm_h, original_rgb=original_rgb)
    attacked = attack_image(image_rgb, attack, param)
    after = run_extract(attacked, method, wm_w, wm_h, original_rgb=original_rgb)
    before_wm = _decode(base64.b64decode(before["watermark_png_b64"]), cv2.IMREAD_GRAYSCALE)
    after_wm = _decode(base64.b64decode(after["watermark_png_b64"]), cv2.IMREAD_GRAYSCALE)
    quality = watermark_quality(before_wm, after_wm)
    return {
        "attacked_png_b64": png_b64(attacked),
        "extracted_png_b64": after["watermark_png_b64"],
        "metrics": _capped_quality(image_rgb, attacked),
        "watermark": {"nc": round(quality["nc"], 4), "ber": round(quality["ber"], 4)},
    }
```

- [ ] **Step 4: 跑测试确认通过**

Run: `pytest webapp/backend/tests/test_services.py -v`
Expected: PASS（22 个测试）。若 `test_embed_extract_roundtrip[dwt]` 的 NC 不达 0.85：这是 DWT 盲提取（中值阈值法）在该合成图上的真实表现，属**校准问题而非代码错误**——把 `STRENGTH_RANGES["dwt"]` 默认值在 [0.05, 0.5] 内上调到最小达标值并同步更新本计划 Global Constraints 与前端滑杆默认值，重跑全部测试。

- [ ] **Step 5: Commit**

```bash
git add webapp/backend/services.py webapp/backend/tests/test_services.py
git commit -m "feat: add embed/extract/attack service pipelines"
```

---

### Task 6: /api/embed、/api/extract、/api/attack 路由 + 限流

**Files:**
- Modify: `webapp/backend/routes.py`（重写为完整版）
- Modify: `webapp/backend/app.py`（接入 slowapi）
- Test: `webapp/backend/tests/test_embed_api.py`、`test_extract_api.py`、`test_attack_api.py`、`test_limits.py`

**Interfaces:**
- Consumes: Task 5 的 `run_embed / run_extract / run_attack / decode_host_image / decode_watermark_image / render_text_watermark / read_png_params`。
- Produces（HTTP 契约，前端 `lib/api.ts` 依赖）：
  - `POST /api/embed`（multipart）：`image: file` 必填；`watermark_text: str` 与 `watermark_file: file` 二选一；`method: str`；`strength: float`。200 → run_embed 的 dict 原样。
  - `POST /api/extract`：`image: file` 必填；`method, wm_w, wm_h`（若上传 PNG 带 `watermark-params` 元数据可省略，服务端自动读取）；`original: file` 可选；`reference_watermark: file` 可选。200 → run_extract 的 dict。
  - `POST /api/attack`：`image: file`、`attack: str`、`param: float`、`method, wm_w, wm_h`（同样支持元数据自动读取）、`original: file` 可选。200 → run_attack 的 dict。
  - 三个 POST 均限流 `20/minute`（按 IP），429 返回 `{"error":{"code":"rate_limited","zh":"请求太频繁，请一分钟后再试","en":"Too many requests, try again in a minute"}}`。

- [ ] **Step 1: 写失败测试** `webapp/backend/tests/test_embed_api.py`：

```python
from __future__ import annotations

import base64

from webapp.backend.tests.conftest import encode_png


def _embed(client, synthetic_image, synthetic_watermark, **overrides):
    data = {"method": "dct", "strength": "12.0"}
    data.update({k: v for k, v in overrides.items() if not k.endswith("_file")})
    files = {"image": ("host.png", encode_png(synthetic_image), "image/png")}
    if "watermark_file" in overrides:
        files["watermark_file"] = ("wm.png", overrides["watermark_file"], "image/png")
    return client.post("/api/embed", data=data, files=files)


def test_embed_with_watermark_file(client, synthetic_image, synthetic_watermark):
    response = _embed(client, synthetic_image, synthetic_watermark, watermark_file=encode_png(synthetic_watermark))
    assert response.status_code == 200
    body = response.json()
    assert body["metrics"]["psnr"] > 30
    assert body["params"]["method"] == "dct"
    assert base64.b64decode(body["watermarked_png_b64"])[:8] == b"\x89PNG\r\n\x1a\n"


def test_embed_with_text_watermark(client, synthetic_image, synthetic_watermark):
    response = _embed(client, synthetic_image, synthetic_watermark, watermark_text="水印")
    assert response.status_code == 200


def test_embed_without_watermark_400(client, synthetic_image, synthetic_watermark):
    response = _embed(client, synthetic_image, synthetic_watermark)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "missing_watermark"


def test_embed_bad_method_400(client, synthetic_image, synthetic_watermark):
    response = _embed(client, synthetic_image, synthetic_watermark, watermark_text="hi", method="rsa")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_method"
```

`webapp/backend/tests/test_extract_api.py`：

```python
from __future__ import annotations

import base64

from webapp.backend.tests.conftest import encode_png


def _embedded_png(client, synthetic_image, synthetic_watermark, method="dct", strength="12.0"):
    response = client.post(
        "/api/embed",
        data={"method": method, "strength": strength},
        files={
            "image": ("host.png", encode_png(synthetic_image), "image/png"),
            "watermark_file": ("wm.png", encode_png(synthetic_watermark), "image/png"),
        },
    )
    assert response.status_code == 200
    return base64.b64decode(response.json()["watermarked_png_b64"])


def test_extract_autoreads_png_params(client, synthetic_image, synthetic_watermark):
    watermarked = _embedded_png(client, synthetic_image, synthetic_watermark)
    response = client.post(
        "/api/extract",
        files={
            "image": ("wm.png", watermarked, "image/png"),
            "reference_watermark": ("ref.png", encode_png(synthetic_watermark), "image/png"),
        },
    )
    assert response.status_code == 200
    assert response.json()["nc"] > 0.85


def test_extract_dft_missing_original_422(client, synthetic_image, synthetic_watermark):
    watermarked = _embedded_png(client, synthetic_image, synthetic_watermark, method="dft", strength="10.0")
    response = client.post("/api/extract", files={"image": ("wm.png", watermarked, "image/png")})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "dft_requires_original"


def test_extract_without_params_or_meta_400(client, synthetic_image):
    response = client.post("/api/extract", files={"image": ("x.png", encode_png(synthetic_image), "image/png")})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "missing_params"
```

`webapp/backend/tests/test_attack_api.py`：

```python
from __future__ import annotations

import base64

from webapp.backend.tests.conftest import encode_png
from webapp.backend.tests.test_extract_api import _embedded_png


def test_attack_jpeg_reports_watermark_quality(client, synthetic_image, synthetic_watermark):
    watermarked = _embedded_png(client, synthetic_image, synthetic_watermark)
    response = client.post(
        "/api/attack",
        data={"attack": "jpeg", "param": "90"},
        files={"image": ("wm.png", watermarked, "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert 0.0 <= body["watermark"]["ber"] <= 1.0
    assert base64.b64decode(body["attacked_png_b64"])


def test_attack_bad_type_400(client, synthetic_image, synthetic_watermark):
    watermarked = _embedded_png(client, synthetic_image, synthetic_watermark)
    response = client.post(
        "/api/attack",
        data={"attack": "steal", "param": "1"},
        files={"image": ("wm.png", watermarked, "image/png")},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_attack"
```

`webapp/backend/tests/test_limits.py`：

```python
from __future__ import annotations


def test_rate_limit_returns_bilingual_429(client, synthetic_image):
    from webapp.backend.tests.conftest import encode_png

    payload = {"files": {"image": ("x.png", encode_png(synthetic_image), "image/png")}}
    last = None
    for _ in range(25):
        last = client.post("/api/extract", **payload)
        if last.status_code == 429:
            break
    assert last is not None and last.status_code == 429
    assert last.json()["error"]["code"] == "rate_limited"
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pytest webapp/backend/tests -v`
Expected: 新增测试 FAIL（404 / 缺少 missing_params 错误码）

- [ ] **Step 3: 实现**

`webapp/backend/errors.py` 追加：

```python
def missing_params() -> ApiError:
    return ApiError(400, "missing_params", "该 PNG 不含参数信息，请手动选择算法与水印尺寸", "This PNG has no embedded params; choose method and watermark size manually")


def rate_limited() -> ApiError:
    return ApiError(429, "rate_limited", "请求太频繁，请一分钟后再试", "Too many requests, try again in a minute")
```

`webapp/backend/routes.py` 重写：

```python
from __future__ import annotations

from fastapi import APIRouter, File, Form, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address

from webapp.backend import errors, services

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


async def _read(upload: UploadFile | None) -> bytes | None:
    if upload is None:
        return None
    data = await upload.read()
    return data or None


def _resolve_params(data: bytes, method: str | None, wm_w: int | None, wm_h: int | None) -> tuple[str, int, int]:
    if method and wm_w and wm_h:
        return method, int(wm_w), int(wm_h)
    meta = services.read_png_params(data)
    if meta and meta.get("v") == 1:
        return str(meta["method"]), int(meta["wm_w"]), int(meta["wm_h"])
    raise errors.missing_params()


@router.post("/embed")
@limiter.limit("20/minute")
async def embed(
    request: Request,
    image: UploadFile = File(...),
    method: str = Form("dct"),
    strength: float = Form(...),
    watermark_text: str | None = Form(None),
    watermark_file: UploadFile | None = File(None),
) -> dict:
    host = services.decode_host_image(await image.read())
    wm_bytes = await _read(watermark_file)
    if wm_bytes is not None:
        watermark = services.decode_watermark_image(wm_bytes)
    elif watermark_text and watermark_text.strip():
        watermark = services.render_text_watermark(watermark_text)
    else:
        raise errors.missing_watermark()
    return services.run_embed(host, watermark, method, strength)


@router.post("/extract")
@limiter.limit("20/minute")
async def extract(
    request: Request,
    image: UploadFile = File(...),
    method: str | None = Form(None),
    wm_w: int | None = Form(None),
    wm_h: int | None = Form(None),
    original: UploadFile | None = File(None),
    reference_watermark: UploadFile | None = File(None),
) -> dict:
    data = await image.read()
    resolved_method, width, height = _resolve_params(data, method, wm_w, wm_h)
    original_bytes = await _read(original)
    reference_bytes = await _read(reference_watermark)
    return services.run_extract(
        services.decode_host_image(data),
        resolved_method,
        width,
        height,
        original_rgb=services.decode_host_image(original_bytes) if original_bytes else None,
        reference_watermark=services.decode_watermark_image(reference_bytes) if reference_bytes else None,
    )


@router.post("/attack")
@limiter.limit("20/minute")
async def attack(
    request: Request,
    image: UploadFile = File(...),
    attack: str = Form(...),
    param: float = Form(...),
    method: str | None = Form(None),
    wm_w: int | None = Form(None),
    wm_h: int | None = Form(None),
    original: UploadFile | None = File(None),
) -> dict:
    data = await image.read()
    resolved_method, width, height = _resolve_params(data, method, wm_w, wm_h)
    original_bytes = await _read(original)
    return services.run_attack(
        services.decode_host_image(data),
        attack,
        param,
        resolved_method,
        width,
        height,
        original_rgb=services.decode_host_image(original_bytes) if original_bytes else None,
    )
```

`webapp/backend/app.py`：`create_app()` 里 `app.include_router(...)` 之前接入 slowapi——

```python
from slowapi.errors import RateLimitExceeded

from webapp.backend.routes import limiter
# create_app() 内：
    app.state.limiter = limiter

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        from webapp.backend.errors import rate_limited

        err = rate_limited()
        return JSONResponse(status_code=err.status, content=err.payload())
```

- [ ] **Step 4: 跑全部后端测试**

Run: `pytest webapp/backend/tests -v`
Expected: 全部 PASS。注意：限流按进程内存计数，测试顺序可能使先跑的用例触发 429——若出现，在 conftest.py 的 `client` fixture 里每次 `limiter.reset()`（`from webapp.backend.routes import limiter`），test_limits.py 单独构造未 reset 的 client。

- [ ] **Step 5: 手动冒烟**

```bash
uvicorn webapp.backend.app:app --port 8000 &
sleep 2 && curl -s localhost:8000/api/health
kill %1
```
Expected: `{"status":"ok"}`

- [ ] **Step 6: Commit**

```bash
git add webapp/backend
git commit -m "feat: add embed/extract/attack API routes with rate limiting"
```

---

### Task 7: 前端脚手架 + 设计 tokens

**Files:**
- Create: `webapp/frontend/package.json`、`vite.config.ts`、`tsconfig.json`、`index.html`
- Create: `webapp/frontend/src/main.tsx`、`src/App.tsx`（临时占位）、`src/styles/tokens.css`
- Create: `webapp/frontend/.gitignore`

**Interfaces:**
- Produces: CSS 自定义属性 `--color-bg/-surface/-ink/-ink-muted/-brand/-brand-deep/-line/-error`（tokens.css，全站唯一颜色来源）；Tailwind v4 主题类（`bg-bg`、`text-ink`、`text-brand` 等）；npm scripts `dev/build/test`。

- [ ] **Step 1: 写文件**

`webapp/frontend/package.json`：

```json
{
  "name": "watermark-studio-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest run"
  },
  "dependencies": {
    "gsap": "^3.12.5",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@tailwindcss/vite": "^4.0.0",
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "tailwindcss": "^4.0.0",
    "typescript": "~5.4.5",
    "vite": "^5.3.1",
    "vitest": "^1.6.0"
  }
}
```

`webapp/frontend/vite.config.ts`：

```ts
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: { "/api": "http://127.0.0.1:8000" },
  },
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
  },
});
```

（vitest 直接读 vite.config 的 `test` 字段；若 tsc 报 `test` 未知属性，把首行改为 `import { defineConfig } from "vitest/config";`）

`webapp/frontend/tsconfig.json`：

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  },
  "include": ["src"]
}
```

`webapp/frontend/index.html`：

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>隐形水印工坊 · Invisible Watermark Studio</title>
    <meta name="description" content="把水印藏进图像的频率里——免费的 DFT/DCT/DWT 频域水印在线体验" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@600;700&family=STIX+Two+Text:wght@600;700&display=swap"
      rel="stylesheet"
    />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

`webapp/frontend/src/styles/tokens.css`（值来自根目录 DESIGN.md）：

```css
@import "tailwindcss";

@theme {
  --color-bg: oklch(0.97 0.003 170);
  --color-surface: oklch(0.995 0.002 170);
  --color-ink: oklch(0.22 0.01 170);
  --color-ink-muted: oklch(0.45 0.015 170);
  --color-brand: oklch(0.45 0.09 170);
  --color-brand-deep: oklch(0.32 0.07 172);
  --color-line: oklch(0.9 0.004 170);
  --color-error: oklch(0.55 0.19 25);
  --font-display: "Noto Serif SC", "STIX Two Text", serif;
  --font-body: -apple-system, "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
}

html {
  scroll-behavior: smooth;
}

body {
  background: var(--color-bg);
  color: var(--color-ink);
  font-family: var(--font-body);
}

h1,
h2,
h3 {
  font-family: var(--font-display);
  text-wrap: balance;
}

@media (prefers-reduced-motion: reduce) {
  html {
    scroll-behavior: auto;
  }
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

:focus-visible {
  outline: 2px solid var(--color-brand);
  outline-offset: 2px;
}
```

`webapp/frontend/src/main.tsx`：

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles/tokens.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

`webapp/frontend/src/App.tsx`（占位，Task 13/15 会重写）：

```tsx
export default function App() {
  return <main className="min-h-screen bg-bg text-ink p-10 font-body">Invisible Watermark Studio</main>;
}
```

`webapp/frontend/.gitignore`：

```
node_modules
dist
```

- [ ] **Step 2: 安装并验证构建**

```bash
cd webapp/frontend && npm install && npm run build
```
Expected: `dist/` 生成，无 TS 错误。

- [ ] **Step 3: Commit**

```bash
git add webapp/frontend
git commit -m "feat: scaffold Vite React frontend with design tokens"
```

---

### Task 8: i18n 模块 + 全量双语文案

**Files:**
- Create: `webapp/frontend/src/i18n/zh.ts`、`src/i18n/en.ts`、`src/i18n/index.tsx`
- Create: `webapp/frontend/src/components/LangToggle.tsx`
- Test: `webapp/frontend/src/i18n/i18n.test.ts`

**Interfaces:**
- Produces: `type Dict = typeof zh`；`LangProvider`、`useI18n(): { t: Dict; lang: "zh" | "en"; setLang(l): void }`；文案键结构见 zh.ts（en.ts 必须同构）。

- [ ] **Step 1: 写失败测试** `webapp/frontend/src/i18n/i18n.test.ts`：

```ts
import { describe, expect, it } from "vitest";
import { en } from "./en";
import { zh } from "./zh";

function keysOf(obj: Record<string, unknown>, prefix = ""): string[] {
  return Object.entries(obj).flatMap(([k, v]) =>
    typeof v === "object" && v !== null ? keysOf(v as Record<string, unknown>, `${prefix}${k}.`) : [`${prefix}${k}`],
  );
}

describe("i18n dictionaries", () => {
  it("zh and en have identical key sets", () => {
    expect(keysOf(en).sort()).toEqual(keysOf(zh).sort());
  });
  it("no empty strings", () => {
    for (const dict of [zh, en]) {
      const walk = (o: Record<string, unknown>): void =>
        Object.values(o).forEach((v) =>
          typeof v === "object" && v !== null ? walk(v as Record<string, unknown>) : expect(String(v).trim()).not.toBe(""),
        );
      walk(dict);
    }
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd webapp/frontend && npm test`
Expected: FAIL（模块不存在）

- [ ] **Step 3: 实现**

`webapp/frontend/src/i18n/zh.ts`：

```ts
export const zh = {
  nav: { brand: "隐形水印工坊", story: "原理", tool: "开始体验", github: "GitHub" },
  hero: {
    title: "把水印藏进图像的频率里",
    subtitle: "肉眼看不见，提取得回来，攻击不掉——基于 DFT / DCT / DWT 的频域水印在线体验",
    cta: "看看它如何工作",
    scrollHint: "向下滚动",
  },
  story: {
    s1: { title: "这是一张普通的照片", body: "至少看起来是。接下来的一分钟，我们会往里面藏一段谁也看不见的信息。" },
    s2: { title: "但图像其实是波的叠加", body: "对它做一次傅里叶变换，像素就变成了频率——低频是轮廓，高频是细节。" },
    s3: { title: "水印写进中频系数", body: "太低伤画质，太高易丢失。中频是隐蔽性与鲁棒性的平衡点。" },
    s4: { title: "变回像素世界", body: "逆变换回来，画面几乎分毫未动——差值放大 20 倍才勉强可见。", metric: "峰值信噪比" },
    s5: { title: "现在，攻击它", body: "JPEG 压缩、缩放、加噪——日常传播中图片会经历的一切。" },
    s6: { title: "水印依然在", body: "从被攻击的图像里，仍然能把水印提取回来。", metric: "归一化相关系数" },
    s7: { title: "轮到你了", body: "上传你的图片，写下你的名字，亲手把它藏进频率里。", cta: "开始嵌入" },
  },
  workbench: {
    title: "工作台",
    tabs: { embed: "嵌入", extract: "提取", attack: "攻击实验室" },
    privacy: "图片全程在内存中处理，服务器不保存任何数据。",
    sizeNote: "为保护免费算力，输出图像最长边为 1024 像素。",
    waking: "免费服务器正在唤醒，大约需要 30 秒……",
    processing: "处理中……",
    failed: "请求失败，请重试",
    useSample: "用示例图试试",
    download: "下载",
    dropHint: "拖入图片，或点击选择",
    fileTypes: "支持 JPG / PNG / WebP / TIFF，≤ 10MB",
  },
  embed: {
    watermarkLabel: "你的水印",
    textMode: "文字",
    imageMode: "图片",
    textPlaceholder: "输入水印文字，如：© 侯治民 2026",
    methodLabel: "算法",
    methods: {
      dct: { name: "DCT", hint: "推荐 · 盲提取，抗 JPEG 强" },
      dft: { name: "DFT", hint: "非盲 · 提取时需要原图" },
      dwt: { name: "DWT", hint: "多分辨率 · 嵌入演示（盲提取不可靠）" },
    },
    strengthLabel: "嵌入强度",
    strengthHint: "越强越鲁棒，越弱画质越好",
    submit: "嵌入水印",
    resultTitle: "嵌入完成",
    psnr: "PSNR（画质）",
    ssim: "SSIM（结构相似度）",
    spectrumBefore: "嵌入前频谱",
    spectrumAfter: "嵌入后频谱",
    downloadNote: "下载的 PNG 已内置提取参数，提取页拖入即可自动识别。",
    toExtract: "去提取验证 →",
  },
  extract: {
    intro: "上传含水印的图片。由本工坊生成的 PNG 会自动识别参数。",
    autoDetected: "已从图片中读取参数",
    manualTitle: "手动参数",
    wmSizeLabel: "水印尺寸",
    originalLabel: "原图（DFT 必需）",
    originalHint: "DFT 是非盲算法，需要对比原图才能提取",
    referenceLabel: "原始水印（可选，用于计算相似度）",
    submit: "提取水印",
    resultTitle: "提取结果",
    nc: "NC（相似度）",
    ber: "BER（误码率）",
  },
  attack: {
    intro: "攻击一张含水印的图，看水印能不能扛住。",
    useLast: "使用刚才的嵌入结果",
    attackLabel: "攻击方式",
    types: {
      jpeg: { name: "JPEG 压缩", param: "压缩质量" },
      resize: { name: "缩放", param: "缩放比例" },
      noise: { name: "高斯噪声", param: "噪声强度 σ" },
    },
    submit: "发起攻击",
    attackedTitle: "攻击后的图像",
    extractedTitle: "攻击后提取的水印",
    qualityTitle: "图像质量变化",
    survivalTitle: "水印存活度",
  },
  footer: {
    tagline: "一个信号与系统课程项目的延伸",
    source: "查看源码",
    stack: "FastAPI × React × Hugging Face Spaces · 免费运行",
  },
  errors: { network: "网络异常，请检查连接后重试", timeout: "请求超时，服务器可能正在唤醒，请稍后重试" },
};

export type Dict = typeof zh;
```

（注意：不要写 `as const`——那会把 `Dict` 锁成中文字面量类型，导致 en.ts 无法通过类型检查。）

`webapp/frontend/src/i18n/en.ts`（同构，`export const en: Dict = { ... }`）：

```ts
import type { Dict } from "./zh";

export const en: Dict = {
  nav: { brand: "Invisible Watermark Studio", story: "How it works", tool: "Try it", github: "GitHub" },
  hero: {
    title: "Hide a watermark inside the frequencies of an image",
    subtitle: "Invisible to the eye, recoverable on demand, robust to attacks — DFT / DCT / DWT frequency-domain watermarking, live",
    cta: "See how it works",
    scrollHint: "Scroll",
  },
  story: {
    s1: { title: "This is an ordinary photo", body: "Or so it seems. Over the next minute we will hide a message inside it that no one can see." },
    s2: { title: "An image is a sum of waves", body: "Apply a Fourier transform and pixels become frequencies — low ones carry shape, high ones carry detail." },
    s3: { title: "The watermark goes into the mid-band", body: "Too low hurts quality; too high gets destroyed. The mid-band balances invisibility and robustness." },
    s4: { title: "Back to the pixel world", body: "After the inverse transform the picture is virtually untouched — the difference is barely visible even amplified 20×.", metric: "Peak signal-to-noise ratio" },
    s5: { title: "Now, attack it", body: "JPEG compression, rescaling, noise — everything an image endures in the wild." },
    s6: { title: "The watermark survives", body: "From the attacked image, the watermark can still be pulled back out.", metric: "Normalized correlation" },
    s7: { title: "Your turn", body: "Upload your picture, write your name, and hide it in the frequencies yourself.", cta: "Start embedding" },
  },
  workbench: {
    title: "Workbench",
    tabs: { embed: "Embed", extract: "Extract", attack: "Attack lab" },
    privacy: "Images are processed entirely in memory; the server stores nothing.",
    sizeNote: "To protect free compute, output images are capped at 1024px on the long side.",
    waking: "Waking up the free server, about 30 seconds…",
    processing: "Processing…",
    failed: "Request failed, please retry",
    useSample: "Try a sample image",
    download: "Download",
    dropHint: "Drop an image, or click to choose",
    fileTypes: "JPG / PNG / WebP / TIFF, ≤ 10MB",
  },
  embed: {
    watermarkLabel: "Your watermark",
    textMode: "Text",
    imageMode: "Image",
    textPlaceholder: "Watermark text, e.g. © Zhimin Hou 2026",
    methodLabel: "Algorithm",
    methods: {
      dct: { name: "DCT", hint: "Recommended · blind extraction, JPEG-robust" },
      dft: { name: "DFT", hint: "Non-blind · needs the original to extract" },
      dwt: { name: "DWT", hint: "Multi-resolution · embedding demo (blind extraction unreliable)" },
    },
    strengthLabel: "Embedding strength",
    strengthHint: "Stronger is more robust; weaker preserves quality",
    submit: "Embed watermark",
    resultTitle: "Embedded",
    psnr: "PSNR (quality)",
    ssim: "SSIM (structural similarity)",
    spectrumBefore: "Spectrum before",
    spectrumAfter: "Spectrum after",
    downloadNote: "The downloaded PNG carries its extraction params — drop it on the Extract tab and they fill in automatically.",
    toExtract: "Verify by extracting →",
  },
  extract: {
    intro: "Upload a watermarked image. PNGs made by this studio are recognized automatically.",
    autoDetected: "Parameters read from the image",
    manualTitle: "Manual parameters",
    wmSizeLabel: "Watermark size",
    originalLabel: "Original image (required for DFT)",
    originalHint: "DFT is non-blind: extraction compares against the original",
    referenceLabel: "Original watermark (optional, for similarity metrics)",
    submit: "Extract watermark",
    resultTitle: "Extraction result",
    nc: "NC (similarity)",
    ber: "BER (bit error rate)",
  },
  attack: {
    intro: "Attack a watermarked image and see if the watermark survives.",
    useLast: "Use the result you just embedded",
    attackLabel: "Attack",
    types: {
      jpeg: { name: "JPEG compression", param: "Quality" },
      resize: { name: "Rescaling", param: "Scale factor" },
      noise: { name: "Gaussian noise", param: "Noise σ" },
    },
    submit: "Launch attack",
    attackedTitle: "Attacked image",
    extractedTitle: "Watermark extracted after attack",
    qualityTitle: "Image quality change",
    survivalTitle: "Watermark survival",
  },
  footer: {
    tagline: "An extension of a Signals & Systems course project",
    source: "View source",
    stack: "FastAPI × React × Hugging Face Spaces · runs free",
  },
  errors: { network: "Network error — check your connection and retry", timeout: "Request timed out; the server may be waking up, please retry shortly" },
};
```

`webapp/frontend/src/i18n/index.tsx`：

```tsx
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { en } from "./en";
import { zh, type Dict } from "./zh";

type Lang = "zh" | "en";
const dicts: Record<Lang, Dict> = { zh, en };

const I18nContext = createContext<{ t: Dict; lang: Lang; setLang: (l: Lang) => void }>({
  t: zh,
  lang: "zh",
  setLang: () => {},
});

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>(() => (localStorage.getItem("lang") === "en" ? "en" : "zh"));
  useEffect(() => {
    localStorage.setItem("lang", lang);
    document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
  }, [lang]);
  return <I18nContext.Provider value={{ t: dicts[lang], lang, setLang }}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  return useContext(I18nContext);
}
```

`webapp/frontend/src/components/LangToggle.tsx`：

```tsx
import { useI18n } from "../i18n";

export default function LangToggle() {
  const { lang, setLang } = useI18n();
  return (
    <button
      type="button"
      onClick={() => setLang(lang === "zh" ? "en" : "zh")}
      className="rounded border border-line px-3 py-1 text-sm text-ink-muted transition-colors duration-200 hover:border-brand hover:text-brand"
      aria-label={lang === "zh" ? "Switch to English" : "切换到中文"}
    >
      {lang === "zh" ? "EN" : "中文"}
    </button>
  );
}
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd webapp/frontend && npm test && npm run build`
Expected: 2 个测试 PASS，构建成功。

- [ ] **Step 5: Commit**

```bash
git add webapp/frontend/src
git commit -m "feat: add bilingual i18n with full copy and parity test"
```

---

### Task 9: API 客户端 + PNG 元数据解析器

**Files:**
- Create: `webapp/frontend/src/lib/api.ts`、`src/lib/pngMeta.ts`
- Test: `webapp/frontend/src/lib/api.test.ts`、`src/lib/pngMeta.test.ts`

**Interfaces:**
- Consumes: Task 6 的 HTTP 契约。
- Produces:
  - `pngMeta.ts`: `readWatermarkParams(buffer: ArrayBuffer) -> WmParams | null`；`type WmParams = { v: 1; method: "dct" | "dft" | "dwt"; strength: number; wm_w: number; wm_h: number }`
  - `api.ts`: `type ApiError = { code: string; zh: string; en: string }`；`class ApiFailure extends Error { detail: ApiError }`；`embed(form: FormData): Promise<EmbedResponse>`；`extract(form: FormData): Promise<ExtractResponse>`；`attack(form: FormData): Promise<AttackResponse>`；`waitForHealth(timeoutMs?: number): Promise<boolean>`；响应类型字段与后端 JSON 一一对应（`EmbedResponse = { watermarked_png_b64: string; metrics: { psnr: number; ssim: number }; spectrum_before_b64: string; spectrum_after_b64: string; params: WmParams; prepared_watermark_png_b64: string }`；`ExtractResponse = { watermark_png_b64: string; nc?: number; ber?: number }`；`AttackResponse = { attacked_png_b64: string; extracted_png_b64: string; metrics: { psnr: number; ssim: number }; watermark: { nc: number; ber: number } }`）。

- [ ] **Step 1: 写失败测试**

`webapp/frontend/src/lib/pngMeta.test.ts`（测试内自建含 tEXt 的最小合法 PNG）：

```ts
import { describe, expect, it } from "vitest";
import { readWatermarkParams } from "./pngMeta";

const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(bytes: Uint8Array): number {
  let c = 0xffffffff;
  for (const b of bytes) c = CRC_TABLE[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function chunk(type: string, data: Uint8Array): Uint8Array {
  const out = new Uint8Array(12 + data.length);
  const view = new DataView(out.buffer);
  view.setUint32(0, data.length);
  const typed = new Uint8Array(4 + data.length);
  typed.set(new TextEncoder().encode(type), 0);
  typed.set(data, 4);
  out.set(typed, 4);
  view.setUint32(8 + data.length, crc32(typed));
  return out;
}

function buildPng(withParams: boolean): ArrayBuffer {
  const sig = new Uint8Array([137, 80, 78, 71, 13, 10, 26, 10]);
  const ihdr = chunk("IHDR", new Uint8Array([0, 0, 0, 1, 0, 0, 0, 1, 8, 0, 0, 0, 0]));
  const params = JSON.stringify({ v: 1, method: "dct", strength: 12, wm_w: 64, wm_h: 64 });
  const textData = new TextEncoder().encode(`watermark-params\0${params}`);
  const text = chunk("tEXt", textData);
  const iend = chunk("IEND", new Uint8Array(0));
  const parts = withParams ? [sig, ihdr, text, iend] : [sig, ihdr, iend];
  const total = parts.reduce((n, p) => n + p.length, 0);
  const buffer = new Uint8Array(total);
  let offset = 0;
  for (const part of parts) {
    buffer.set(part, offset);
    offset += part.length;
  }
  return buffer.buffer;
}

describe("readWatermarkParams", () => {
  it("reads params from tEXt chunk", () => {
    expect(readWatermarkParams(buildPng(true))).toEqual({ v: 1, method: "dct", strength: 12, wm_w: 64, wm_h: 64 });
  });
  it("returns null when absent", () => {
    expect(readWatermarkParams(buildPng(false))).toBeNull();
  });
  it("returns null for non-PNG", () => {
    expect(readWatermarkParams(new TextEncoder().encode("not a png").buffer)).toBeNull();
  });
});
```

`webapp/frontend/src/lib/api.test.ts`：

```ts
import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiFailure, embed } from "./api";

afterEach(() => vi.unstubAllGlobals());

describe("api client", () => {
  it("returns parsed JSON on 200", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ params: { method: "dct" } }), { status: 200 })));
    const body = await embed(new FormData());
    expect(body.params.method).toBe("dct");
  });
  it("throws ApiFailure with bilingual detail on error status", async () => {
    const payload = { error: { code: "bad_method", zh: "算法错误", en: "Bad method" } };
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify(payload), { status: 400 })));
    await expect(embed(new FormData())).rejects.toSatisfy((e: unknown) => e instanceof ApiFailure && e.detail.code === "bad_method");
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd webapp/frontend && npm test`
Expected: FAIL（模块不存在）

- [ ] **Step 3: 实现**

`webapp/frontend/src/lib/pngMeta.ts`：

```ts
export type WmParams = { v: 1; method: "dct" | "dft" | "dwt"; strength: number; wm_w: number; wm_h: number };

const PNG_SIG = [137, 80, 78, 71, 13, 10, 26, 10];
const KEYWORD = "watermark-params";

export function readWatermarkParams(buffer: ArrayBuffer): WmParams | null {
  const bytes = new Uint8Array(buffer);
  if (bytes.length < 16 || PNG_SIG.some((v, i) => bytes[i] !== v)) return null;
  const view = new DataView(buffer);
  let offset = 8;
  while (offset + 12 <= bytes.length) {
    const length = view.getUint32(offset);
    const type = String.fromCharCode(...bytes.subarray(offset + 4, offset + 8));
    if (type === "tEXt") {
      const data = bytes.subarray(offset + 8, offset + 8 + length);
      const separator = data.indexOf(0);
      if (separator > 0) {
        const keyword = new TextDecoder("latin1").decode(data.subarray(0, separator));
        if (keyword === KEYWORD) {
          try {
            const parsed = JSON.parse(new TextDecoder().decode(data.subarray(separator + 1)));
            if (parsed && parsed.v === 1 && ["dct", "dft", "dwt"].includes(parsed.method)) return parsed as WmParams;
          } catch {
            return null;
          }
        }
      }
    }
    if (type === "IEND") break;
    offset += 12 + length;
  }
  return null;
}
```

`webapp/frontend/src/lib/api.ts`：

```ts
import type { WmParams } from "./pngMeta";

export type ApiError = { code: string; zh: string; en: string };

export class ApiFailure extends Error {
  detail: ApiError;
  constructor(detail: ApiError) {
    super(detail.code);
    this.detail = detail;
  }
}

export type EmbedResponse = {
  watermarked_png_b64: string;
  metrics: { psnr: number; ssim: number };
  spectrum_before_b64: string;
  spectrum_after_b64: string;
  params: WmParams;
  prepared_watermark_png_b64: string;
};

export type ExtractResponse = { watermark_png_b64: string; nc?: number; ber?: number };

export type AttackResponse = {
  attacked_png_b64: string;
  extracted_png_b64: string;
  metrics: { psnr: number; ssim: number };
  watermark: { nc: number; ber: number };
};

async function post<T>(path: string, form: FormData): Promise<T> {
  let response: Response;
  try {
    response = await fetch(path, { method: "POST", body: form, signal: AbortSignal.timeout(45_000) });
  } catch (cause) {
    const code = cause instanceof DOMException && cause.name === "TimeoutError" ? "timeout" : "network";
    throw new ApiFailure({ code, zh: "", en: "" });
  }
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiFailure(body?.error ?? { code: "network", zh: "", en: "" });
  }
  return body as T;
}

export const embed = (form: FormData) => post<EmbedResponse>("/api/embed", form);
export const extract = (form: FormData) => post<ExtractResponse>("/api/extract", form);
export const attack = (form: FormData) => post<AttackResponse>("/api/attack", form);

export async function waitForHealth(timeoutMs = 90_000): Promise<boolean> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const response = await fetch("/api/health", { signal: AbortSignal.timeout(4_000) });
      if (response.ok) return true;
    } catch {
      /* keep polling */
    }
    await new Promise((resolve) => setTimeout(resolve, 2_500));
  }
  return false;
}
```

（`ApiFailure` 的 `code` 为 `network`/`timeout` 时 zh/en 为空串，由组件层用 `t.errors.network`/`t.errors.timeout` 兜底显示。）

- [ ] **Step 4: 跑测试确认通过**

Run: `cd webapp/frontend && npm test`
Expected: 全部 PASS（i18n 2 + pngMeta 3 + api 2）

- [ ] **Step 5: Commit**

```bash
git add webapp/frontend/src/lib
git commit -m "feat: add typed API client and PNG metadata parser"
```

---

### Task 10: 共享组件 + 工作台状态

**Files:**
- Create: `webapp/frontend/src/state/workbench.tsx`
- Create: `webapp/frontend/src/components/Dropzone.tsx`、`MethodPicker.tsx`、`StrengthSlider.tsx`、`MetricRow.tsx`、`ResultImage.tsx`

**Interfaces:**
- Consumes: `useI18n`、`WmParams`。
- Produces:
  - `WorkbenchProvider` / `useWorkbench(): { lastEmbed: LastEmbed | null; setLastEmbed(v): void; activeTab: TabKey; setActiveTab(k): void }`；`type LastEmbed = { pngB64: string; params: WmParams }`；`type TabKey = "embed" | "extract" | "attack"`
  - `<Dropzone value onChange accept?>`（含拖放、键盘可用、预览缩略图）
  - `<MethodPicker value onChange />`、`<StrengthSlider method value onChange />`（范围与 Global Constraints 一致）
  - `<MetricRow label value />`、`<ResultImage b64 alt downloadName? label? />`

- [ ] **Step 1: 实现**（纯展示/状态组件，由 Task 11–13 的使用 + 构建验证，无独立单测）

`webapp/frontend/src/state/workbench.tsx`：

```tsx
import { createContext, useContext, useState, type ReactNode } from "react";
import type { WmParams } from "../lib/pngMeta";

export type LastEmbed = { pngB64: string; params: WmParams };
export type TabKey = "embed" | "extract" | "attack";

const WorkbenchContext = createContext<{
  lastEmbed: LastEmbed | null;
  setLastEmbed: (v: LastEmbed | null) => void;
  activeTab: TabKey;
  setActiveTab: (k: TabKey) => void;
}>({ lastEmbed: null, setLastEmbed: () => {}, activeTab: "embed", setActiveTab: () => {} });

export function WorkbenchProvider({ children }: { children: ReactNode }) {
  const [lastEmbed, setLastEmbed] = useState<LastEmbed | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>("embed");
  return (
    <WorkbenchContext.Provider value={{ lastEmbed, setLastEmbed, activeTab, setActiveTab }}>
      {children}
    </WorkbenchContext.Provider>
  );
}

export const useWorkbench = () => useContext(WorkbenchContext);
```

`webapp/frontend/src/components/Dropzone.tsx`：

```tsx
import { useEffect, useRef, useState } from "react";
import { useI18n } from "../i18n";

type Props = { value: File | null; onChange: (f: File) => void; accept?: string; label?: string };

export default function Dropzone({ value, onChange, accept = "image/*", label }: Props) {
  const { t } = useI18n();
  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  useEffect(() => {
    if (!value) return setPreview(null);
    const url = URL.createObjectURL(value);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [value]);

  return (
    <button
      type="button"
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer.files[0];
        if (file) onChange(file);
      }}
      className={`flex min-h-40 w-full flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-4 transition-colors duration-200 ${
        dragging ? "border-brand bg-surface" : "border-line bg-surface hover:border-brand"
      }`}
    >
      {preview ? (
        <img src={preview} alt={value?.name ?? ""} className="max-h-48 rounded" />
      ) : (
        <>
          <span className="text-ink">{label ?? t.workbench.dropHint}</span>
          <span className="text-sm text-ink-muted">{t.workbench.fileTypes}</span>
        </>
      )}
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => e.target.files?.[0] && onChange(e.target.files[0])}
      />
    </button>
  );
}
```

`webapp/frontend/src/components/MethodPicker.tsx`：

```tsx
import { useI18n } from "../i18n";

type Method = "dct" | "dft" | "dwt";
const METHODS: Method[] = ["dct", "dft", "dwt"];

export default function MethodPicker({ value, onChange }: { value: Method; onChange: (m: Method) => void }) {
  const { t } = useI18n();
  return (
    <div role="radiogroup" aria-label={t.embed.methodLabel} className="grid grid-cols-1 gap-2 sm:grid-cols-3">
      {METHODS.map((method) => (
        <button
          key={method}
          type="button"
          role="radio"
          aria-checked={value === method}
          onClick={() => onChange(method)}
          className={`rounded-lg border p-3 text-left transition-colors duration-200 ${
            value === method ? "border-brand bg-surface" : "border-line bg-surface hover:border-brand"
          }`}
        >
          <div className={`font-semibold ${value === method ? "text-brand" : "text-ink"}`}>{t.embed.methods[method].name}</div>
          <div className="text-sm text-ink-muted">{t.embed.methods[method].hint}</div>
        </button>
      ))}
    </div>
  );
}
```

`webapp/frontend/src/components/StrengthSlider.tsx`：

```tsx
import { useI18n } from "../i18n";

export const STRENGTH_RANGES = {
  dct: { min: 4, max: 24, step: 1, default: 12 },
  dft: { min: 2, max: 20, step: 1, default: 3 },
  dwt: { min: 0.01, max: 0.5, step: 0.01, default: 0.05 },
} as const;

type Method = keyof typeof STRENGTH_RANGES;

export default function StrengthSlider({ method, value, onChange }: { method: Method; value: number; onChange: (v: number) => void }) {
  const { t } = useI18n();
  const range = STRENGTH_RANGES[method];
  return (
    <label className="block">
      <div className="flex justify-between text-sm">
        <span className="text-ink">{t.embed.strengthLabel}</span>
        <span className="tabular-nums text-brand">{value}</span>
      </div>
      <input
        type="range"
        min={range.min}
        max={range.max}
        step={range.step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-(--color-brand)"
      />
      <div className="text-xs text-ink-muted">{t.embed.strengthHint}</div>
    </label>
  );
}
```

（若执行时 `STRENGTH_RANGES["dwt"].default` 在 Task 5 校准中改过，这里同步改成相同值。）

`webapp/frontend/src/components/MetricRow.tsx`：

```tsx
export default function MetricRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-baseline justify-between border-b border-line py-2">
      <span className="text-sm text-ink-muted">{label}</span>
      <span className="font-display text-xl tabular-nums text-ink">{value}</span>
    </div>
  );
}
```

`webapp/frontend/src/components/ResultImage.tsx`：

```tsx
import { useI18n } from "../i18n";

type Props = { b64: string; alt: string; downloadName?: string; label?: string };

export default function ResultImage({ b64, alt, downloadName, label }: Props) {
  const { t } = useI18n();
  const src = `data:image/png;base64,${b64}`;
  return (
    <figure className="space-y-2">
      <img src={src} alt={alt} className="w-full rounded-lg border border-line bg-surface" />
      <figcaption className="flex items-center justify-between text-sm text-ink-muted">
        <span>{label ?? alt}</span>
        {downloadName && (
          <a href={src} download={downloadName} className="rounded bg-brand px-3 py-1 text-white transition-colors duration-200 hover:bg-brand-deep">
            {t.workbench.download}
          </a>
        )}
      </figcaption>
    </figure>
  );
}
```

- [ ] **Step 2: 验证构建**

Run: `cd webapp/frontend && npm run build`
Expected: 通过（组件暂未被引用，tsconfig `noUnusedLocals` 只查文件内未用变量，不报未引用文件）。

- [ ] **Step 3: Commit**

```bash
git add webapp/frontend/src/state webapp/frontend/src/components
git commit -m "feat: add workbench state and shared UI components"
```

---

### Task 11: 嵌入标签页

**Files:**
- Create: `webapp/frontend/src/sections/workbench/EmbedTab.tsx`

**Interfaces:**
- Consumes: `embed()`、`Dropzone/MethodPicker/StrengthSlider/MetricRow/ResultImage`、`useWorkbench`、`useI18n`、`STRENGTH_RANGES`。
- Produces: `<EmbedTab />`；成功后调用 `setLastEmbed({ pngB64, params })`。

- [ ] **Step 1: 实现** `webapp/frontend/src/sections/workbench/EmbedTab.tsx`：

```tsx
import { useState } from "react";
import Dropzone from "../../components/Dropzone";
import MethodPicker from "../../components/MethodPicker";
import MetricRow from "../../components/MetricRow";
import ResultImage from "../../components/ResultImage";
import StrengthSlider, { STRENGTH_RANGES } from "../../components/StrengthSlider";
import { useI18n } from "../../i18n";
import { ApiFailure, embed, type EmbedResponse } from "../../lib/api";
import { useWorkbench } from "../../state/workbench";

type Method = "dct" | "dft" | "dwt";

export default function EmbedTab() {
  const { t, lang } = useI18n();
  const { setLastEmbed, setActiveTab } = useWorkbench();
  const [image, setImage] = useState<File | null>(null);
  const [mode, setMode] = useState<"text" | "image">("text");
  const [text, setText] = useState("");
  const [wmFile, setWmFile] = useState<File | null>(null);
  const [method, setMethod] = useState<Method>("dct");
  const [strength, setStrength] = useState<number>(STRENGTH_RANGES.dct.default);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<EmbedResponse | null>(null);

  const pickMethod = (m: Method) => {
    setMethod(m);
    setStrength(STRENGTH_RANGES[m].default);
  };

  const useSample = async () => {
    const response = await fetch("/samples/sample1.jpg");
    const blob = await response.blob();
    setImage(new File([blob], "sample1.jpg", { type: "image/jpeg" }));
  };

  const submit = async () => {
    if (!image) return;
    setBusy(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("image", image);
      form.append("method", method);
      form.append("strength", String(strength));
      if (mode === "text") form.append("watermark_text", text);
      else if (wmFile) form.append("watermark_file", wmFile);
      const body = await embed(form);
      setResult(body);
      setLastEmbed({ pngB64: body.watermarked_png_b64, params: body.params });
    } catch (cause) {
      if (cause instanceof ApiFailure) {
        const fallback = cause.detail.code === "timeout" ? t.errors.timeout : t.errors.network;
        setError(cause.detail[lang] || fallback);
      } else setError(t.workbench.failed);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      <div className="space-y-6">
        <div className="space-y-2">
          <Dropzone value={image} onChange={setImage} />
          <button type="button" onClick={useSample} className="text-sm text-brand underline-offset-4 hover:underline">
            {t.workbench.useSample}
          </button>
        </div>
        <fieldset className="space-y-2">
          <legend className="text-sm font-semibold text-ink">{t.embed.watermarkLabel}</legend>
          <div role="tablist" className="flex gap-2">
            {(["text", "image"] as const).map((m) => (
              <button
                key={m}
                type="button"
                role="tab"
                aria-selected={mode === m}
                onClick={() => setMode(m)}
                className={`rounded px-3 py-1 text-sm transition-colors duration-200 ${
                  mode === m ? "bg-brand text-white" : "border border-line text-ink-muted hover:border-brand"
                }`}
              >
                {m === "text" ? t.embed.textMode : t.embed.imageMode}
              </button>
            ))}
          </div>
          {mode === "text" ? (
            <input
              type="text"
              maxLength={20}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={t.embed.textPlaceholder}
              className="w-full rounded border border-line bg-surface p-2 text-ink placeholder:text-ink-muted"
            />
          ) : (
            <Dropzone value={wmFile} onChange={setWmFile} />
          )}
        </fieldset>
        <fieldset className="space-y-2">
          <legend className="text-sm font-semibold text-ink">{t.embed.methodLabel}</legend>
          <MethodPicker value={method} onChange={pickMethod} />
        </fieldset>
        <StrengthSlider method={method} value={strength} onChange={setStrength} />
        <button
          type="button"
          disabled={busy || !image || (mode === "text" ? !text.trim() : !wmFile)}
          onClick={submit}
          className="w-full rounded-lg bg-brand py-3 font-semibold text-white transition-colors duration-200 hover:bg-brand-deep disabled:opacity-40"
        >
          {busy ? t.workbench.processing : t.embed.submit}
        </button>
        {error && <p role="alert" className="text-sm text-error">{error}</p>}
      </div>
      <div className="space-y-4" aria-live="polite">
        {result && (
          <>
            <h3 className="text-xl text-ink">{t.embed.resultTitle}</h3>
            <ResultImage b64={result.watermarked_png_b64} alt={t.embed.resultTitle} downloadName="watermarked.png" />
            <p className="text-sm text-ink-muted">{t.embed.downloadNote}</p>
            <MetricRow label={t.embed.psnr} value={`${result.metrics.psnr} dB`} />
            <MetricRow label={t.embed.ssim} value={result.metrics.ssim} />
            <div className="grid grid-cols-2 gap-4">
              <ResultImage b64={result.spectrum_before_b64} alt={t.embed.spectrumBefore} />
              <ResultImage b64={result.spectrum_after_b64} alt={t.embed.spectrumAfter} />
            </div>
            <p className="text-sm text-ink-muted">{t.workbench.sizeNote}</p>
            <button type="button" onClick={() => setActiveTab("extract")} className="text-brand underline-offset-4 hover:underline">
              {t.embed.toExtract}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: 验证构建**

Run: `cd webapp/frontend && npm run build`
Expected: 通过。

- [ ] **Step 3: Commit**

```bash
git add webapp/frontend/src/sections
git commit -m "feat: add embed tab"
```

---

### Task 12: 提取 + 攻击标签页

**Files:**
- Create: `webapp/frontend/src/sections/workbench/ExtractTab.tsx`、`AttackTab.tsx`

**Interfaces:**
- Consumes: `extract()/attack()`、`readWatermarkParams`、`useWorkbench().lastEmbed`、共享组件。
- Produces: `<ExtractTab />`、`<AttackTab />`。

- [ ] **Step 1: 实现** `webapp/frontend/src/sections/workbench/ExtractTab.tsx`：

```tsx
import { useState } from "react";
import Dropzone from "../../components/Dropzone";
import MethodPicker from "../../components/MethodPicker";
import MetricRow from "../../components/MetricRow";
import ResultImage from "../../components/ResultImage";
import { useI18n } from "../../i18n";
import { ApiFailure, extract, type ExtractResponse } from "../../lib/api";
import { readWatermarkParams, type WmParams } from "../../lib/pngMeta";

type Method = "dct" | "dft" | "dwt";

export default function ExtractTab() {
  const { t, lang } = useI18n();
  const [image, setImage] = useState<File | null>(null);
  const [meta, setMeta] = useState<WmParams | null>(null);
  const [method, setMethod] = useState<Method>("dct");
  const [side, setSide] = useState(64);
  const [original, setOriginal] = useState<File | null>(null);
  const [reference, setReference] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ExtractResponse | null>(null);

  const onImage = async (file: File) => {
    setImage(file);
    setResult(null);
    const params = readWatermarkParams(await file.arrayBuffer());
    setMeta(params);
    if (params) {
      setMethod(params.method);
      setSide(params.wm_w);
    }
  };

  const effectiveMethod = meta?.method ?? method;

  const submit = async () => {
    if (!image) return;
    setBusy(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("image", image);
      form.append("method", effectiveMethod);
      form.append("wm_w", String(meta?.wm_w ?? side));
      form.append("wm_h", String(meta?.wm_h ?? side));
      if (original) form.append("original", original);
      if (reference) form.append("reference_watermark", reference);
      setResult(await extract(form));
    } catch (cause) {
      if (cause instanceof ApiFailure) {
        const fallback = cause.detail.code === "timeout" ? t.errors.timeout : t.errors.network;
        setError(cause.detail[lang] || fallback);
      } else setError(t.workbench.failed);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      <div className="space-y-6">
        <p className="text-sm text-ink-muted">{t.extract.intro}</p>
        <Dropzone value={image} onChange={onImage} />
        {meta ? (
          <p className="rounded bg-surface p-3 text-sm text-brand">
            {t.extract.autoDetected}：{meta.method.toUpperCase()} · {meta.wm_w}×{meta.wm_h}
          </p>
        ) : (
          <fieldset className="space-y-3">
            <legend className="text-sm font-semibold text-ink">{t.extract.manualTitle}</legend>
            <MethodPicker value={method} onChange={setMethod} />
            <label className="block text-sm text-ink">
              {t.extract.wmSizeLabel}
              <input
                type="number"
                min={8}
                max={64}
                value={side}
                onChange={(e) => setSide(Number(e.target.value))}
                className="ml-2 w-24 rounded border border-line bg-surface p-1 tabular-nums"
              />
            </label>
          </fieldset>
        )}
        {effectiveMethod === "dft" && (
          <fieldset className="space-y-2">
            <legend className="text-sm font-semibold text-ink">{t.extract.originalLabel}</legend>
            <p className="text-xs text-ink-muted">{t.extract.originalHint}</p>
            <Dropzone value={original} onChange={setOriginal} />
          </fieldset>
        )}
        <fieldset className="space-y-2">
          <legend className="text-sm font-semibold text-ink">{t.extract.referenceLabel}</legend>
          <Dropzone value={reference} onChange={setReference} />
        </fieldset>
        <button
          type="button"
          disabled={busy || !image || (effectiveMethod === "dft" && !original)}
          onClick={submit}
          className="w-full rounded-lg bg-brand py-3 font-semibold text-white transition-colors duration-200 hover:bg-brand-deep disabled:opacity-40"
        >
          {busy ? t.workbench.processing : t.extract.submit}
        </button>
        {error && <p role="alert" className="text-sm text-error">{error}</p>}
      </div>
      <div className="space-y-4" aria-live="polite">
        {result && (
          <>
            <h3 className="text-xl text-ink">{t.extract.resultTitle}</h3>
            <ResultImage b64={result.watermark_png_b64} alt={t.extract.resultTitle} downloadName="extracted.png" />
            {result.nc !== undefined && <MetricRow label={t.extract.nc} value={result.nc} />}
            {result.ber !== undefined && <MetricRow label={t.extract.ber} value={result.ber} />}
          </>
        )}
      </div>
    </div>
  );
}
```

`webapp/frontend/src/sections/workbench/AttackTab.tsx`：

```tsx
import { useState } from "react";
import Dropzone from "../../components/Dropzone";
import MetricRow from "../../components/MetricRow";
import ResultImage from "../../components/ResultImage";
import { useI18n } from "../../i18n";
import { ApiFailure, attack, type AttackResponse } from "../../lib/api";
import { useWorkbench } from "../../state/workbench";

const ATTACK_RANGES = {
  jpeg: { min: 10, max: 100, step: 5, default: 60 },
  resize: { min: 0.3, max: 1, step: 0.05, default: 0.5 },
  noise: { min: 2, max: 30, step: 1, default: 10 },
} as const;

type AttackKey = keyof typeof ATTACK_RANGES;

function base64ToFile(b64: string, name: string): File {
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return new File([bytes], name, { type: "image/png" });
}

export default function AttackTab() {
  const { t, lang } = useI18n();
  const { lastEmbed } = useWorkbench();
  const [image, setImage] = useState<File | null>(null);
  const [attackType, setAttackType] = useState<AttackKey>("jpeg");
  const [param, setParam] = useState<number>(ATTACK_RANGES.jpeg.default);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AttackResponse | null>(null);

  const pickAttack = (key: AttackKey) => {
    setAttackType(key);
    setParam(ATTACK_RANGES[key].default);
  };

  const submit = async () => {
    if (!image) return;
    setBusy(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("image", image);
      form.append("attack", attackType);
      form.append("param", String(param));
      setResult(await attack(form));
    } catch (cause) {
      if (cause instanceof ApiFailure) {
        const fallback = cause.detail.code === "timeout" ? t.errors.timeout : t.errors.network;
        setError(cause.detail[lang] || fallback);
      } else setError(t.workbench.failed);
    } finally {
      setBusy(false);
    }
  };

  const range = ATTACK_RANGES[attackType];

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      <div className="space-y-6">
        <p className="text-sm text-ink-muted">{t.attack.intro}</p>
        {lastEmbed && (
          <button
            type="button"
            onClick={() => setImage(base64ToFile(lastEmbed.pngB64, "watermarked.png"))}
            className="rounded border border-brand px-3 py-1 text-sm text-brand transition-colors duration-200 hover:bg-brand hover:text-white"
          >
            {t.attack.useLast}
          </button>
        )}
        <Dropzone value={image} onChange={setImage} />
        <fieldset className="space-y-2">
          <legend className="text-sm font-semibold text-ink">{t.attack.attackLabel}</legend>
          <div role="radiogroup" className="flex flex-wrap gap-2">
            {(Object.keys(ATTACK_RANGES) as AttackKey[]).map((key) => (
              <button
                key={key}
                type="button"
                role="radio"
                aria-checked={attackType === key}
                onClick={() => pickAttack(key)}
                className={`rounded px-3 py-1 text-sm transition-colors duration-200 ${
                  attackType === key ? "bg-brand text-white" : "border border-line text-ink-muted hover:border-brand"
                }`}
              >
                {t.attack.types[key].name}
              </button>
            ))}
          </div>
          <label className="block">
            <div className="flex justify-between text-sm">
              <span className="text-ink">{t.attack.types[attackType].param}</span>
              <span className="tabular-nums text-brand">{param}</span>
            </div>
            <input
              type="range"
              min={range.min}
              max={range.max}
              step={range.step}
              value={param}
              onChange={(e) => setParam(Number(e.target.value))}
              className="w-full accent-(--color-brand)"
            />
          </label>
        </fieldset>
        <button
          type="button"
          disabled={busy || !image}
          onClick={submit}
          className="w-full rounded-lg bg-brand py-3 font-semibold text-white transition-colors duration-200 hover:bg-brand-deep disabled:opacity-40"
        >
          {busy ? t.workbench.processing : t.attack.submit}
        </button>
        {error && <p role="alert" className="text-sm text-error">{error}</p>}
      </div>
      <div className="space-y-4" aria-live="polite">
        {result && (
          <>
            <ResultImage b64={result.attacked_png_b64} alt={t.attack.attackedTitle} label={t.attack.attackedTitle} />
            <ResultImage b64={result.extracted_png_b64} alt={t.attack.extractedTitle} label={t.attack.extractedTitle} />
            <h4 className="text-sm font-semibold text-ink">{t.attack.qualityTitle}</h4>
            <MetricRow label="PSNR" value={`${result.metrics.psnr} dB`} />
            <MetricRow label="SSIM" value={result.metrics.ssim} />
            <h4 className="text-sm font-semibold text-ink">{t.attack.survivalTitle}</h4>
            <MetricRow label={t.extract.nc} value={result.watermark.nc} />
            <MetricRow label={t.extract.ber} value={result.watermark.ber} />
          </>
        )}
      </div>
    </div>
  );
}
```

（攻击请求不带 method/wm 参数——工坊产出的 PNG 内含 `watermark-params` 元数据，后端 `_resolve_params` 自动读取；DFT 场景攻击页暂不支持补传原图，界面依赖元数据即可，DFT 的攻击实验通过「先嵌入再一键复用」路径完成，此时元数据存在。）

- [ ] **Step 2: 验证构建**

Run: `cd webapp/frontend && npm run build`
Expected: 通过。

- [ ] **Step 3: Commit**

```bash
git add webapp/frontend/src/sections
git commit -m "feat: add extract and attack tabs"
```

---

### Task 13: 工作台外壳 + 冷启动兜底 + 页面组装

**Files:**
- Create: `webapp/frontend/src/components/ColdStartGate.tsx`
- Create: `webapp/frontend/src/sections/workbench/Workbench.tsx`
- Create: `webapp/frontend/src/sections/Footer.tsx`
- Modify: `webapp/frontend/src/App.tsx`（重写）

**Interfaces:**
- Consumes: `waitForHealth`、三个 Tab、`useWorkbench`、`LangProvider`、`LangToggle`。
- Produces: `<Workbench />`（id="workbench"，供叙事 CTA 锚点跳转）；`<ColdStartGate>` 包裹工作台内容；组装后的 App（导航 + 占位 hero + 工作台 + footer，Task 15 替换占位 hero 为完整叙事）。

- [ ] **Step 1: 实现**

`webapp/frontend/src/components/ColdStartGate.tsx`：

```tsx
import { useEffect, useState, type ReactNode } from "react";
import { useI18n } from "../i18n";
import { waitForHealth } from "../lib/api";

export default function ColdStartGate({ children }: { children: ReactNode }) {
  const { t } = useI18n();
  const [ready, setReady] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const fast = await waitForHealth(2_000);
      if (!cancelled && fast) return setReady(true);
      if (!cancelled) setReady(false);
      const eventually = await waitForHealth(120_000);
      if (!cancelled) setReady(eventually);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (ready) return <>{children}</>;
  return (
    <div className="flex min-h-60 flex-col items-center justify-center gap-3 rounded-lg border border-line bg-surface p-8">
      <div className="h-1 w-48 overflow-hidden rounded bg-line" role="progressbar" aria-label={t.workbench.waking}>
        <div className="h-full w-1/3 animate-pulse bg-brand" />
      </div>
      <p className="text-sm text-ink-muted">{ready === null ? t.workbench.processing : t.workbench.waking}</p>
    </div>
  );
}
```

`webapp/frontend/src/sections/workbench/Workbench.tsx`：

```tsx
import ColdStartGate from "../../components/ColdStartGate";
import { useI18n } from "../../i18n";
import { useWorkbench, type TabKey } from "../../state/workbench";
import AttackTab from "./AttackTab";
import EmbedTab from "./EmbedTab";
import ExtractTab from "./ExtractTab";

const TABS: TabKey[] = ["embed", "extract", "attack"];

export default function Workbench() {
  const { t } = useI18n();
  const { activeTab, setActiveTab } = useWorkbench();
  return (
    <section id="workbench" className="mx-auto max-w-5xl px-4 py-16 sm:px-6">
      <h2 className="mb-2 text-3xl text-ink">{t.workbench.title}</h2>
      <p className="mb-8 text-sm text-ink-muted">{t.workbench.privacy}</p>
      <div role="tablist" aria-label={t.workbench.title} className="mb-8 flex gap-1 border-b border-line">
        {TABS.map((key) => (
          <button
            key={key}
            type="button"
            role="tab"
            aria-selected={activeTab === key}
            onClick={() => setActiveTab(key)}
            className={`px-4 py-2 font-semibold transition-colors duration-200 ${
              activeTab === key ? "border-b-2 border-brand text-brand" : "text-ink-muted hover:text-ink"
            }`}
          >
            {t.workbench.tabs[key]}
          </button>
        ))}
      </div>
      <ColdStartGate>
        {activeTab === "embed" && <EmbedTab />}
        {activeTab === "extract" && <ExtractTab />}
        {activeTab === "attack" && <AttackTab />}
      </ColdStartGate>
    </section>
  );
}
```

`webapp/frontend/src/sections/Footer.tsx`：

```tsx
import { useI18n } from "../i18n";

export default function Footer() {
  const { t } = useI18n();
  return (
    <footer className="border-t border-line py-10 text-center text-sm text-ink-muted">
      <p>{t.footer.tagline}</p>
      <p className="mt-1">
        <a href="https://github.com" className="text-brand underline-offset-4 hover:underline">
          {t.footer.source}
        </a>
        {" · "}
        {t.footer.stack}
      </p>
    </footer>
  );
}
```

（GitHub 链接在 Task 17 部署时替换为真实仓库地址。）

`webapp/frontend/src/App.tsx` 重写：

```tsx
import LangToggle from "./components/LangToggle";
import { LangProvider, useI18n } from "./i18n";
import Footer from "./sections/Footer";
import Workbench from "./sections/workbench/Workbench";
import { WorkbenchProvider } from "./state/workbench";

function Nav() {
  const { t } = useI18n();
  return (
    <header className="sticky top-0 z-30 border-b border-line bg-bg/90 backdrop-blur-sm">
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3 sm:px-6">
        <span className="font-display font-semibold text-ink">{t.nav.brand}</span>
        <div className="flex items-center gap-4 text-sm">
          <a href="#workbench" className="text-ink-muted hover:text-brand">
            {t.nav.tool}
          </a>
          <LangToggle />
        </div>
      </nav>
    </header>
  );
}

function PlaceholderHero() {
  const { t } = useI18n();
  return (
    <section className="mx-auto max-w-5xl px-4 py-24 text-center sm:px-6">
      <h1 className="text-4xl text-ink sm:text-5xl">{t.hero.title}</h1>
      <p className="mx-auto mt-4 max-w-xl text-ink-muted">{t.hero.subtitle}</p>
    </section>
  );
}

export default function App() {
  return (
    <LangProvider>
      <WorkbenchProvider>
        <Nav />
        <main>
          <PlaceholderHero />
          <Workbench />
        </main>
        <Footer />
      </WorkbenchProvider>
    </LangProvider>
  );
}
```

- [ ] **Step 2: 端到端手动验证**（后端 + 前端一起跑）

```bash
uvicorn webapp.backend.app:app --port 8000 &
cd webapp/frontend && npm run dev
```
浏览器打开 http://localhost:5173：上传任意图片 → 输入文字水印 → 嵌入 → 看到指标与频谱 → 下载 PNG → 提取页拖入 → 自动识别参数 → 提取成功 → 攻击页「使用刚才的嵌入结果」→ JPEG 60 攻击 → 看到存活度指标。全流程无控制台报错后 `kill %1`。

- [ ] **Step 3: 跑全部测试**

Run: `cd webapp/frontend && npm test && npm run build && cd ../.. && pytest webapp/backend/tests -q`
Expected: 全部 PASS。

- [ ] **Step 4: Commit**

```bash
git add webapp/frontend/src
git commit -m "feat: assemble workbench with cold-start gate and app shell"
```

---

### Task 14: 叙事素材离线生成

**Files:**
- Create: `webapp/scripts/gen_story_assets.py`
- Create（脚本产出，提交进仓库）: `webapp/frontend/public/story/*.png`、`story.json`、`webapp/frontend/public/samples/sample1.jpg`、`sample2.jpg`

**Interfaces:**
- Consumes: `webapp.backend.services`、`watermarking.io_utils.read_color`。
- Produces（前端 Story 组件依赖的静态资源契约）：`/story/01-photo.png, 02-spectrum.png, 03-spectrum-marked.png, 04-watermarked.png, 04-diff20.png, 05-attacked.png, 06-extracted.png` 与 `/story/story.json = { "psnr": number, "ssim": number, "nc": number }`；`/samples/sample1.jpg`。

- [ ] **Step 1: 实现** `webapp/scripts/gen_story_assets.py`：

```python
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
    outcome = services.run_attack(watermarked, "jpeg", 40, "dct", side, side)
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
```

- [ ] **Step 2: 运行并验证**

```bash
python webapp/scripts/gen_story_assets.py && ls webapp/frontend/public/story webapp/frontend/public/samples
```
Expected: 7 个 PNG + story.json + 至少 sample1.jpg；`cat webapp/frontend/public/story/story.json` 里 psnr > 30、nc > 0.5。若 nc ≤ 0.5，把攻击质量参数从 40 提到 60 重新生成（叙事数字必须真实且好看）。

- [ ] **Step 3: Commit**

```bash
git add webapp/scripts webapp/frontend/public
git commit -m "feat: generate scrollytelling assets from real algorithm output"
```

---

### Task 15: 滚动叙事 + Hero + 墨绿过渡段

**Files:**
- Create: `webapp/frontend/src/sections/Hero.tsx`、`storyData.ts`、`Story.tsx`、`StoryStatic.tsx`、`CtaBridge.tsx`
- Modify: `webapp/frontend/src/App.tsx`（替换 PlaceholderHero）

**Interfaces:**
- Consumes: Task 14 的静态资源契约、`useI18n`、gsap + ScrollTrigger。
- Produces: `storyData.ts` 导出 `SCENES`、`type StoryMetrics`、`useStoryMetrics()`（Story 与 StoryStatic 共用，避免循环导入）；`<Hero />`、`<Story />`（内部自动在 reduced-motion 或 <768px 时渲染 `<StoryStatic />`）、`<CtaBridge />`。

- [ ] **Step 1: 实现**

`webapp/frontend/src/sections/Hero.tsx`：

```tsx
import { useI18n } from "../i18n";

export default function Hero() {
  const { t } = useI18n();
  return (
    <section className="mx-auto flex min-h-[85vh] max-w-5xl flex-col items-center justify-center px-4 text-center sm:px-6">
      <h1 className="max-w-3xl text-4xl leading-tight text-ink sm:text-6xl">{t.hero.title}</h1>
      <p className="mt-6 max-w-xl text-lg text-ink-muted">{t.hero.subtitle}</p>
      <a
        href="#story"
        className="mt-10 rounded-lg bg-brand px-6 py-3 font-semibold text-white transition-colors duration-200 hover:bg-brand-deep"
      >
        {t.hero.cta}
      </a>
      <div aria-hidden className="mt-16 animate-bounce text-ink-muted">
        ↓ {t.hero.scrollHint}
      </div>
    </section>
  );
}
```

`webapp/frontend/src/sections/storyData.ts`（场景数据与指标 hook，Story/StoryStatic 共用）：

```ts
import { useEffect, useState } from "react";

export type StoryMetrics = { psnr: number; ssim: number; nc: number };

export type SceneKey = "s1" | "s2" | "s3" | "s4" | "s5" | "s6";

export const SCENES: {
  key: SceneKey;
  image: string;
  extraImage?: string;
  metric?: (m: StoryMetrics) => string;
}[] = [
  { key: "s1", image: "/story/01-photo.png" },
  { key: "s2", image: "/story/02-spectrum.png" },
  { key: "s3", image: "/story/03-spectrum-marked.png" },
  { key: "s4", image: "/story/04-watermarked.png", extraImage: "/story/04-diff20.png", metric: (m) => `PSNR ${m.psnr} dB` },
  { key: "s5", image: "/story/05-attacked.png" },
  { key: "s6", image: "/story/06-extracted.png", metric: (m) => `NC ${m.nc}` },
];

export function useStoryMetrics(): StoryMetrics | null {
  const [metrics, setMetrics] = useState<StoryMetrics | null>(null);
  useEffect(() => {
    fetch("/story/story.json")
      .then((r) => r.json())
      .then(setMetrics)
      .catch(() => setMetrics(null));
  }, []);
  return metrics;
}
```

`webapp/frontend/src/sections/StoryStatic.tsx`（移动端 / reduced-motion 版本）：

```tsx
import { useI18n } from "../i18n";
import { SCENES, useStoryMetrics } from "./storyData";

export default function StoryStatic() {
  const { t } = useI18n();
  const metrics = useStoryMetrics();
  return (
    <div className="mx-auto max-w-2xl space-y-16 px-4 py-16 sm:px-6">
      {SCENES.map((scene) => {
        const copy = t.story[scene.key];
        return (
          <figure key={scene.key} className="space-y-3">
            <img src={scene.image} alt={copy.title} className="w-full rounded-lg border border-line" loading="lazy" />
            {scene.extraImage && <img src={scene.extraImage} alt="" className="w-full rounded-lg border border-line" loading="lazy" />}
            <figcaption>
              <h3 className="text-2xl text-ink">{copy.title}</h3>
              <p className="mt-1 text-ink-muted">{copy.body}</p>
              {scene.metric && metrics && (
                <p className="mt-2 font-display text-3xl tabular-nums text-brand">{scene.metric(metrics)}</p>
              )}
            </figcaption>
          </figure>
        );
      })}
    </div>
  );
}
```

`webapp/frontend/src/sections/Story.tsx`：

```tsx
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { useI18n } from "../i18n";
import { SCENES, useStoryMetrics } from "./storyData";
import StoryStatic from "./StoryStatic";

gsap.registerPlugin(ScrollTrigger);

function usePinnedStory() {
  const [pinned, setPinned] = useState(true);
  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const narrow = window.matchMedia("(max-width: 767px)");
    const update = () => setPinned(!media.matches && !narrow.matches);
    update();
    media.addEventListener("change", update);
    narrow.addEventListener("change", update);
    return () => {
      media.removeEventListener("change", update);
      narrow.removeEventListener("change", update);
    };
  }, []);
  return pinned;
}

function PinnedStory() {
  const { t } = useI18n();
  const metrics = useStoryMetrics();
  const containerRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const context = gsap.context(() => {
      const panels = gsap.utils.toArray<HTMLElement>("[data-scene]");
      const frames = gsap.utils.toArray<HTMLElement>("[data-frame]");
      gsap.set(frames.slice(1), { autoAlpha: 0 });
      gsap.set(panels.slice(1), { autoAlpha: 0, y: 24 });
      const timeline = gsap.timeline({
        scrollTrigger: {
          trigger: container,
          start: "top top",
          end: `+=${SCENES.length * 90}%`,
          pin: true,
          scrub: 0.6,
        },
      });
      for (let index = 1; index < SCENES.length; index++) {
        timeline
          .to(panels[index - 1], { autoAlpha: 0, y: -24, duration: 0.4 }, index)
          .to(frames[index - 1], { autoAlpha: 0, duration: 0.4 }, index)
          .to(panels[index], { autoAlpha: 1, y: 0, duration: 0.4 }, index + 0.1)
          .to(frames[index], { autoAlpha: 1, duration: 0.4 }, index + 0.1);
      }
    }, container);
    return () => context.revert();
  }, []);

  return (
    <div ref={containerRef} className="relative min-h-screen">
      <div className="mx-auto grid h-screen max-w-5xl grid-cols-2 items-center gap-12 px-6">
        <div className="relative">
          {SCENES.map((scene) => {
            const copy = t.story[scene.key];
            return (
              <div key={scene.key} data-scene className="absolute inset-x-0 top-1/2 -translate-y-1/2">
                <h3 className="text-3xl text-ink">{copy.title}</h3>
                <p className="mt-3 max-w-md text-lg text-ink-muted">{copy.body}</p>
                {scene.metric && metrics && (
                  <p className="mt-4 font-display text-4xl tabular-nums text-brand">{scene.metric(metrics)}</p>
                )}
              </div>
            );
          })}
        </div>
        <div className="relative aspect-square">
          {SCENES.map((scene) => (
            <div key={scene.key} data-frame className="absolute inset-0 flex flex-col justify-center gap-3">
              <img src={scene.image} alt="" className="max-h-[70vh] w-full rounded-lg border border-line object-contain" />
              {scene.extraImage && (
                <img src={scene.extraImage} alt="" className="max-h-[20vh] w-full rounded-lg border border-line object-contain" />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function Story() {
  const pinned = usePinnedStory();
  return <section id="story">{pinned ? <PinnedStory /> : <StoryStatic />}</section>;
}
```

`webapp/frontend/src/sections/CtaBridge.tsx`（全站唯一 Drenched 段落）：

```tsx
import { useI18n } from "../i18n";

export default function CtaBridge() {
  const { t } = useI18n();
  return (
    <section className="bg-brand-deep py-28 text-center">
      <h2 className="text-4xl text-white sm:text-5xl">{t.story.s7.title}</h2>
      <p className="mx-auto mt-4 max-w-md text-lg text-white/80">{t.story.s7.body}</p>
      <a
        href="#workbench"
        className="mt-10 inline-block rounded-lg bg-white px-8 py-3 font-semibold text-brand-deep transition-colors duration-200 hover:bg-bg"
      >
        {t.story.s7.cta}
      </a>
    </section>
  );
}
```

`webapp/frontend/src/App.tsx`：删除 `PlaceholderHero`，`<main>` 改为：

```tsx
import Hero from "./sections/Hero";
import Story from "./sections/Story";
import CtaBridge from "./sections/CtaBridge";
// ...
        <main>
          <Hero />
          <Story />
          <CtaBridge />
          <Workbench />
        </main>
```

同时给 Nav 增加 `<a href="#story">{t.nav.story}</a>` 链接（放在 `#workbench` 链接前）。

- [ ] **Step 2: 手动验证**

```bash
uvicorn webapp.backend.app:app --port 8000 &
cd webapp/frontend && npm run dev
```
桌面宽度：滚动经过叙事段，画面钉住、6 幕依次交叉淡入、PSNR/NC 数字来自 story.json；墨绿段 CTA 点击滚到工作台。DevTools 切 375px 宽 + 模拟 prefers-reduced-motion：叙事变为纵向静态分段。无控制台报错。`kill %1`

- [ ] **Step 3: 测试 + 构建**

Run: `cd webapp/frontend && npm test && npm run build`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add webapp/frontend/src
git commit -m "feat: add scrollytelling story, hero and drenched CTA bridge"
```

---

### Task 16: Docker 镜像

**Files:**
- Create: `Dockerfile`（仓库根）
- Create: `.dockerignore`

**Interfaces:**
- Produces: 监听 7860 端口的自包含镜像；HF Spaces 直接以此构建。

- [ ] **Step 1: 写文件**

`Dockerfile`：

```dockerfile
FROM node:20-slim AS frontend
WORKDIR /build
COPY webapp/frontend/package.json webapp/frontend/package-lock.json ./
RUN npm ci
COPY webapp/frontend ./
RUN npm run build

FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends fonts-noto-cjk && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY webapp/backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY src /app/src
COPY webapp/backend /app/webapp/backend
COPY --from=frontend /build/dist /app/webapp/frontend/dist
ENV PYTHONPATH=/app:/app/src
EXPOSE 7860
CMD ["uvicorn", "webapp.backend.app:app", "--host", "0.0.0.0", "--port", "7860"]
```

`.dockerignore`：

```
.git
.venv
.worktrees
.superpowers
.pytest_cache
__pycache__
**/node_modules
webapp/frontend/dist
outputs
data
docs
submission_package
*.pdf
*.zip
*.tiff
```

- [ ] **Step 2: 构建并冒烟**（需要本机 Docker；没有就跳过本步，在 HF 上验证）

```bash
docker build -t watermark-studio . && docker run -d -p 7860:7860 --name wm-test watermark-studio
sleep 5 && curl -s localhost:7860/api/health && curl -s -o /dev/null -w "%{http_code}\n" localhost:7860/
docker rm -f wm-test
```
Expected: `{"status":"ok"}` 与 `200`（静态首页可访问）。

- [ ] **Step 3: Commit**

```bash
git add Dockerfile .dockerignore
git commit -m "chore: add multi-stage Dockerfile for HF Spaces"
```

---

### Task 17: CI/CD 与 Hugging Face Space 上线

**Files:**
- Create: `.github/workflows/deploy.yml`
- Modify: `README.md`（顶部加 HF front-matter）
- Modify: `webapp/frontend/src/sections/Footer.tsx`（替换真实 GitHub 地址）

**Interfaces:**
- Consumes: GitHub 仓库 + HF 账号（用户手动创建，见 Step 3）。
- Produces: push main → 测试 → 自动同步到 HF Space。

- [ ] **Step 1: README.md 顶部插入**（第 1 行起，原内容整体下移）：

```markdown
---
title: Invisible Watermark Studio
emoji: 🌊
colorFrom: green
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

```

- [ ] **Step 2: 写 `.github/workflows/deploy.yml`**：

```yaml
name: test-and-deploy

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: sudo apt-get update && sudo apt-get install -y fonts-noto-cjk
      - run: pip install -r webapp/backend/requirements.txt pytest==8.0.2 httpx==0.27.0
      - run: pytest webapp/backend/tests -q
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: webapp/frontend/package-lock.json
      - run: npm ci
        working-directory: webapp/frontend
      - run: npm test
        working-directory: webapp/frontend
      - run: npm run build
        working-directory: webapp/frontend

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Push to Hugging Face Space
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
          HF_SPACE: ${{ vars.HF_SPACE }}
        run: |
          git push --force "https://user:${HF_TOKEN}@huggingface.co/spaces/${HF_SPACE}" HEAD:main
```

- [ ] **Step 3: 上线操作（需要用户账号，执行者停下来向用户展示以下步骤并等待完成）**

1. GitHub 建仓库并推送本项目（若尚未推送）。
2. https://huggingface.co/new-space → 名称如 `invisible-watermark-studio`，SDK 选 **Docker**，Public。
3. HF Settings → Access Tokens → 新建 **write** 权限 token。
4. GitHub 仓库 Settings → Secrets and variables → Actions：新建 secret `HF_TOKEN`（粘贴 token）、variable `HF_SPACE`（值如 `你的用户名/invisible-watermark-studio`）。
5. 把 `Footer.tsx` 里的 `https://github.com` 改成真实仓库地址。
6. push main，等 Action 绿灯，打开 `https://huggingface.co/spaces/<HF_SPACE>` 确认构建成功。

- [ ] **Step 4: Commit**

```bash
git add .github README.md webapp/frontend/src/sections/Footer.tsx
git commit -m "chore: add CI pipeline and HF Space deployment"
```

---

### Task 18: 上线终检（真实浏览器全流程 + 无障碍 + 视觉打磨）

**Files:**
- 无新文件；可能微调 tokens.css / 组件样式。

- [ ] **Step 1: 在已部署的 HF Space URL 上过完整流程**

嵌入（文字水印，中文）→ 下载 → 提取（自动识别）→ 攻击（三种各一次）。手机宽度（375px）重复一遍。记录任何失败并修复后重新部署。

- [ ] **Step 2: 无障碍检查**

- 键盘走查：Tab 能到达每个交互控件，focus 环可见（tokens.css 已定义 `:focus-visible`），Enter/Space 可激活。
- DevTools Rendering → Emulate `prefers-reduced-motion: reduce`：叙事为静态版、无滚动动画。
- 对比度抽查（DevTools 检查器的 contrast 数值）：`--color-ink`/`--color-bg`、`--color-ink-muted`/`--color-bg`、`--color-ink-muted`/`--color-surface`、白字/`--color-brand` 四组必须 ≥ 4.5:1；不达标就加深该 token 并重跑本步。

- [ ] **Step 3: 视觉打磨（impeccable polish 流程）**

按根目录 `DESIGN.md` 的 Bans 清单逐条对照页面；在 1440 / 768 / 375 三档宽度截图检查标题不溢出、间距节奏、叙事图像不变形。发现问题直接修，改动后 `npm test && npm run build` 并重新部署。

- [ ] **Step 4: 最终提交**

```bash
git add -A && git status   # 确认只有预期文件
git commit -m "chore: final polish pass"
git push
```

- [ ] **Step 5: 把最终 URL 交给用户**，附一句冷启动说明（48 小时无访问后首次打开需等待约 30–60 秒）。

