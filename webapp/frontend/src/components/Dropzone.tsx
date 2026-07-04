import { useEffect, useRef, useState } from "react";
import { useI18n } from "../i18n";

type Props = { value: File | null; onChange: (f: File) => void; accept?: string; label?: string };

export default function Dropzone({ value, onChange, accept = "image/*", label }: Props) {
  const { t } = useI18n();
  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  useEffect(() => {
    if (!value) return setPreview(null);
    const url = URL.createObjectURL(value);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [value]);

  return (
    <button
      type="button"
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer.files[0];
        if (file) onChange(file);
      }}
      className={`flex min-h-40 w-full flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-4 transition-colors duration-200 ${
        dragging ? "border-brand bg-surface" : "border-line bg-surface hover:border-brand"
      }`}
    >
      {preview ? (
        <img src={preview} alt={value?.name ?? ""} className="max-h-48 rounded" />
      ) : (
        <>
          <span className="text-ink">{label ?? t.workbench.dropHint}</span>
          <span className="text-sm text-ink-muted">{t.workbench.fileTypes}</span>
        </>
      )}
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => e.target.files?.[0] && onChange(e.target.files[0])}
      />
    </button>
  );
}
