export default function MetricRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-baseline justify-between border-b border-line py-2">
      <span className="text-sm text-ink-muted">{label}</span>
      <span className="font-display text-xl tabular-nums text-ink">{value}</span>
    </div>
  );
}
