import { createContext, useContext, useEffect, useState } from "react";
import { DICT } from "./translations";

export const LANGS = [["en", "EN"], ["ru", "RU"], ["hy", "ՀԱՅ"]];
const Ctx = createContext(null);
export const useLang = () => useContext(Ctx);

export function LangProvider({ children }) {
  const [lang, setLang] = useState(() => localStorage.getItem("lang") || "en");
  useEffect(() => {
    localStorage.setItem("lang", lang);
    document.documentElement.lang = lang;
  }, [lang]);
  // t("English text", {vars}): looks the English text up in the active dictionary; falls back to the text itself.
  const t = (text, vars) => {
    let s = (DICT[lang] && DICT[lang][text]) || text;
    if (vars) for (const k in vars) s = s.replaceAll("{" + k + "}", vars[k]);
    return s;
  };
  return <Ctx.Provider value={{ lang, setLang, t }}>{children}</Ctx.Provider>;
}
