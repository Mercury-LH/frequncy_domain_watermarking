import { useI18n } from "../i18n";

type Props = { b64: string; alt: string; downloadName?: string; label?: string };

export default function ResultImage({ b64, alt, downloadName, label }: Props) {
  const { t } = useI18n();
  const src = `data:image/png;base64,${b64}`;
  return (
    <figure className="space-y-2">
      <img src={src} alt={alt} className="w-full rounded-lg border border-line bg-surface" />
      <figcaption className="flex items-center justify-between text-sm text-ink-muted">
        <span>{label ?? alt}</span>
        {downloadName && (
          <a href={src} download={downloadName} className="rounded bg-brand px-3 py-1 text-white transition-colors duration-200 hover:bg-brand-deep">
            {t.workbench.download}
          </a>
        )}
      </figcaption>
    </figure>
  );
}
