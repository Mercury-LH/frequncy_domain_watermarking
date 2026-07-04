import { useEffect, useState, type ReactNode } from "react";
import { useI18n } from "../i18n";
import { waitForHealth } from "../lib/api";

export default function ColdStartGate({ children }: { children: ReactNode }) {
  const { t } = useI18n();
  const [ready, setReady] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const fast = await waitForHealth(2_000);
      if (!cancelled && fast) return setReady(true);
      if (!cancelled) setReady(false);
      const eventually = await waitForHealth(120_000);
      if (!cancelled) setReady(eventually);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (ready) return <>{children}</>;
  return (
    <div className="flex min-h-60 flex-col items-center justify-center gap-3 rounded-lg border border-line bg-surface p-8">
      <div className="h-1 w-48 overflow-hidden rounded bg-line" role="progressbar" aria-label={t.workbench.waking}>
        <div className="h-full w-1/3 animate-pulse bg-brand" />
      </div>
      <p className="text-sm text-ink-muted">{ready === null ? t.workbench.processing : t.workbench.waking}</p>
    </div>
  );
}
