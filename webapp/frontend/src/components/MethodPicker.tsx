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
