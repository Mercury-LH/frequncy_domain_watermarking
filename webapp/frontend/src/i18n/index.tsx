import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { en } from "./en";
import { zh, type Dict } from "./zh";

type Lang = "zh" | "en";
const dicts: Record<Lang, Dict> = { zh, en };

const I18nContext = createContext<{ t: Dict; lang: Lang; setLang: (l: Lang) => void }>({
  t: zh,
  lang: "zh",
  setLang: () => {},
});

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>(() => (localStorage.getItem("lang") === "en" ? "en" : "zh"));
  useEffect(() => {
    localStorage.setItem("lang", lang);
    document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
  }, [lang]);
  return <I18nContext.Provider value={{ t: dicts[lang], lang, setLang }}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  return useContext(I18nContext);
}
