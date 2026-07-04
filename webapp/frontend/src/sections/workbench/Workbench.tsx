import ColdStartGate from "../../components/ColdStartGate";
import { useI18n } from "../../i18n";
import { useWorkbench, type TabKey } from "../../state/workbench";
import AttackTab from "./AttackTab";
import EmbedTab from "./EmbedTab";
import ExtractTab from "./ExtractTab";

const TABS: TabKey[] = ["embed", "extract", "attack"];

export default function Workbench() {
  const { t } = useI18n();
  const { activeTab, setActiveTab } = useWorkbench();
  return (
    <section id="workbench" className="mx-auto max-w-5xl px-4 py-16 sm:px-6">
      <h2 className="mb-2 text-3xl text-ink">{t.workbench.title}</h2>
      <p className="mb-8 text-sm text-ink-muted">{t.workbench.privacy}</p>
      <div role="tablist" aria-label={t.workbench.title} className="mb-8 flex gap-1 border-b border-line">
        {TABS.map((key) => (
          <button
            key={key}
            type="button"
            role="tab"
            aria-selected={activeTab === key}
            onClick={() => setActiveTab(key)}
            className={`px-4 py-2 font-semibold transition-colors duration-200 ${
              activeTab === key ? "border-b-2 border-brand text-brand" : "text-ink-muted hover:text-ink"
            }`}
          >
            {t.workbench.tabs[key]}
          </button>
        ))}
      </div>
      <ColdStartGate>
        {activeTab === "embed" && <EmbedTab />}
        {activeTab === "extract" && <ExtractTab />}
        {activeTab === "attack" && <AttackTab />}
      </ColdStartGate>
    </section>
  );
}
