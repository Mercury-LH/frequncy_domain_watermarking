import { useI18n } from "../i18n";

export default function LangToggle() {
  const { lang, setLang } = useI18n();
  return (
    <button
      type="button"
      onClick={() => setLang(lang === "zh" ? "en" : "zh")}
      className="rounded border border-line px-3 py-1 text-sm text-ink-muted transition-colors duration-200 hover:border-brand hover:text-brand"
      aria-label={lang === "zh" ? "Switch to English" : "切换到中文"}
    >
      {lang === "zh" ? "EN" : "中文"}
    </button>
  );
}
