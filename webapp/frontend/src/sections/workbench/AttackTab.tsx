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
