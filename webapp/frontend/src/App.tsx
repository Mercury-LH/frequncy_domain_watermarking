import LangToggle from "./components/LangToggle";
import { LangProvider, useI18n } from "./i18n";
import CtaBridge from "./sections/CtaBridge";
import Footer from "./sections/Footer";
import Hero from "./sections/Hero";
import Story from "./sections/Story";
import Workbench from "./sections/workbench/Workbench";
import { WorkbenchProvider } from "./state/workbench";

function Nav() {
  const { t } = useI18n();
  return (
    <header className="sticky top-0 z-30 border-b border-line bg-bg/90 backdrop-blur-sm">
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3 sm:px-6">
        <span className="font-display font-semibold text-ink">{t.nav.brand}</span>
        <div className="flex items-center gap-4 text-sm">
          <a href="#story" className="text-ink-muted hover:text-brand">
            {t.nav.story}
          </a>
          <a href="#workbench" className="text-ink-muted hover:text-brand">
            {t.nav.tool}
          </a>
          <LangToggle />
        </div>
      </nav>
    </header>
  );
}

export default function App() {
  return (
    <LangProvider>
      <WorkbenchProvider>
        <Nav />
        <main>
          <Hero />
          <Story />
          <CtaBridge />
          <Workbench />
        </main>
        <Footer />
      </WorkbenchProvider>
    </LangProvider>
  );
}
