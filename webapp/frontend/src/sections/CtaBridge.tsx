import { useI18n } from "../i18n";

export default function CtaBridge() {
  const { t } = useI18n();
  return (
    <section className="bg-brand-deep py-28 text-center">
      <h2 className="text-4xl text-white sm:text-5xl">{t.story.s7.title}</h2>
      <p className="mx-auto mt-4 max-w-md text-lg text-white/80">{t.story.s7.body}</p>
      <a
        href="#workbench"
        className="mt-10 inline-block rounded-lg bg-white px-8 py-3 font-semibold text-brand-deep transition-colors duration-200 hover:bg-bg"
      >
        {t.story.s7.cta}
      </a>
    </section>
  );
}
