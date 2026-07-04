import LangToggle from "./components/LangToggle";
import { LangProvider, useI18n } from "./i18n";
import Footer from "./sections/Footer";
import Workbench from "./sections/workbench/Workbench";
import { WorkbenchProvider } from "./state/workbench";

function Nav() {
  const { t } = useI18n();
  return (
    <header className="sticky top-0 z-30 border-b border-line bg-bg/90 backdrop-blur-sm">
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3 sm:px-6">
        <span className="font-display font-semibold text-ink">{t.nav.brand}</span>
        <div className="flex items-center gap-4 text-sm">
          <a href="#workbench" className="text-ink-muted hover:text-brand">
            {t.nav.tool}
          </a>
          <LangToggle />
        </div>
      </nav>
    </header>
  );
}

function PlaceholderHero() {
  const { t } = useI18n();
  return (
    <section className="mx-auto max-w-5xl px-4 py-24 text-center sm:px-6">
      <h1 className="text-4xl text-ink sm:text-5xl">{t.hero.title}</h1>
      <p className="mx-auto mt-4 max-w-xl text-ink-muted">{t.hero.subtitle}</p>
    </section>
  );
}

export default function App() {
  return (
    <LangProvider>
      <WorkbenchProvider>
        <Nav />
        <main>
          <PlaceholderHero />
          <Workbench />
        </main>
        <Footer />
      </WorkbenchProvider>
    </LangProvider>
  );
}
