from typing import Optional, Tuple

from fastapi import APIRouter, File, Form, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address

from webapp.backend import errors, services

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


def _check_wm_dim(v: int) -> int:
    if not isinstance(v, int) or not (8 <= v <= 128):
        raise errors.bad_params()
    return v


async def _read(upload: Optional[UploadFile]) -> Optional[bytes]:
    if upload is None:
        return None
    if upload.size is not None and upload.size > services.MAX_BYTES:
        raise errors.file_too_large()
    data = await upload.read()
    return data or None


async def _read_required(upload: UploadFile) -> bytes:
    if upload.size is not None and upload.size > services.MAX_BYTES:
        raise errors.file_too_large()
    return await upload.read()


def _resolve_params(
    data: bytes,
    method: Optional[str],
    wm_w: Optional[int],
    wm_h: Optional[int],
) -> Tuple:
    if method and wm_w and wm_h:
        return method, _check_wm_dim(int(wm_w)), _check_wm_dim(int(wm_h))
    meta = services.read_png_params(data)
    if meta and meta.get("v") == 1:
        return str(meta["method"]), _check_wm_dim(int(meta["wm_w"])), _check_wm_dim(int(meta["wm_h"]))
    raise errors.missing_params()


@router.post("/embed")
@limiter.limit("20/minute")
async def embed(
    request: Request,
    image: UploadFile = File(...),
    method: str = Form("dct"),
    strength: float = Form(...),
    watermark_text: Optional[str] = Form(None),
    watermark_file: Optional[UploadFile] = File(None),
) -> dict:
    host = services.decode_host_image(await _read_required(image))
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
    method: Optional[str] = Form(None),
    wm_w: Optional[int] = Form(None),
    wm_h: Optional[int] = Form(None),
    original: Optional[UploadFile] = File(None),
    reference_watermark: Optional[UploadFile] = File(None),
) -> dict:
    data = await _read_required(image)
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
    method: Optional[str] = Form(None),
    wm_w: Optional[int] = Form(None),
    wm_h: Optional[int] = Form(None),
    original: Optional[UploadFile] = File(None),
) -> dict:
    data = await _read_required(image)
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
