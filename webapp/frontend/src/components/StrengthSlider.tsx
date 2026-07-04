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
