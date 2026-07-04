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


def missing_params() -> ApiError:
    return ApiError(400, "missing_params", "该 PNG 不含参数信息，请手动选择算法与水印尺寸", "This PNG has no embedded params; choose method and watermark size manually")


def rate_limited() -> ApiError:
    return ApiError(429, "rate_limited", "请求太频繁，请一分钟后再试", "Too many requests, try again in a minute")
