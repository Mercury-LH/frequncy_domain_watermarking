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
