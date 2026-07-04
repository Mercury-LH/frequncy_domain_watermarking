import { useI18n } from "../i18n";

export default function Hero() {
  const { t } = useI18n();
  return (
    <section className="mx-auto flex min-h-[85vh] max-w-5xl flex-col items-center justify-center px-4 text-center sm:px-6">
      <h1 className="max-w-3xl text-4xl leading-tight text-ink sm:text-6xl">{t.hero.title}</h1>
      <p className="mt-6 max-w-xl text-lg text-ink-muted">{t.hero.subtitle}</p>
      <a
        href="#story"
        className="mt-10 rounded-lg bg-brand px-6 py-3 font-semibold text-white transition-colors duration-200 hover:bg-brand-deep"
      >
        {t.hero.cta}
      </a>
      <div aria-hidden className="mt-16 flex flex-col items-center gap-2 text-sm text-ink-muted">
        <span>{t.hero.scrollHint}</span>
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.75"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M6 9l6 6 6-6" />
        </svg>
      </div>
    </section>
  );
}
