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
