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
