import { createContext, useContext, useEffect, useState } from "react";

const Ctx = createContext(null);
export const useCart = () => useContext(Ctx);

export function CartProvider({ children }) {
  const [lines, setLines] = useState(() => {
    try { return JSON.parse(localStorage.getItem("cart")) || []; } catch { return []; }
  });
  useEffect(() => { localStorage.setItem("cart", JSON.stringify(lines)); }, [lines]);

  const add = (p) => setLines((ls) => {
    const found = ls.find((l) => l.id === p.id);
    if (found) return ls.map((l) => (l.id === p.id ? { ...l, qty: Math.min(l.qty + 1, 20) } : l));
    return [...ls, { id: p.id, name: p.name, price: p.price, image: p.image, qty: 1 }];
  });
  const setQty = (id, qty) => setLines((ls) => (qty < 1 ? ls.filter((l) => l.id !== id) : ls.map((l) => (l.id === id ? { ...l, qty: Math.min(qty, 20) } : l))));
  const clear = () => setLines([]);
  const count = lines.reduce((n, l) => n + l.qty, 0);
  const total = lines.reduce((n, l) => n + l.qty * l.price, 0);
  return <Ctx.Provider value={{ lines, add, setQty, clear, count, total }}>{children}</Ctx.Provider>;
}
