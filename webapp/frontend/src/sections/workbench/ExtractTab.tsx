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
