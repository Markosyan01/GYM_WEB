import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api } from "./api";

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  const refresh = useCallback(async () => {
    if (!localStorage.getItem("token")) { setUser(null); setReady(true); return; }
    try { setUser(await api("/me")); } catch { localStorage.removeItem("token"); setUser(null); }
    setReady(true);
  }, []);
  useEffect(() => { refresh(); }, [refresh]);

  const sign = async (mode, body) => {
    const { token } = await api("/auth/" + mode, { method: "POST", body });
    localStorage.setItem("token", token);
    await refresh();
  };
  const signOut = () => { localStorage.removeItem("token"); setUser(null); };

  return <Ctx.Provider value={{ user, ready, sign, signOut, refresh }}>{children}</Ctx.Provider>;
}
