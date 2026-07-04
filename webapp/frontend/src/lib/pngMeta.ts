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
