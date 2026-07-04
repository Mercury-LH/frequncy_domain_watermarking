import { useI18n } from "../i18n";

export default function Footer() {
  const { t } = useI18n();
  return (
    <footer className="border-t border-line py-10 text-center text-sm text-ink-muted">
      <p>{t.footer.tagline}</p>
      <p className="mt-1">
        <a href="https://github.com" className="text-brand underline-offset-4 hover:underline">
          {t.footer.source}
        </a>
        {" · "}
        {t.footer.stack}
      </p>
    </footer>
  );
}
