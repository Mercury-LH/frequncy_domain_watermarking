import { createContext, useContext, useState, type ReactNode } from "react";
import type { WmParams } from "../lib/pngMeta";

export type LastEmbed = { pngB64: string; params: WmParams };
export type TabKey = "embed" | "extract" | "attack";

const WorkbenchContext = createContext<{
  lastEmbed: LastEmbed | null;
  setLastEmbed: (v: LastEmbed | null) => void;
  activeTab: TabKey;
  setActiveTab: (k: TabKey) => void;
}>({ lastEmbed: null, setLastEmbed: () => {}, activeTab: "embed", setActiveTab: () => {} });

export function WorkbenchProvider({ children }: { children: ReactNode }) {
  const [lastEmbed, setLastEmbed] = useState<LastEmbed | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>("embed");
  return (
    <WorkbenchContext.Provider value={{ lastEmbed, setLastEmbed, activeTab, setActiveTab }}>
      {children}
    </WorkbenchContext.Provider>
  );
}

export const useWorkbench = () => useContext(WorkbenchContext);
