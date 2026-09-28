import { useState } from "react";

export function Img({ src, alt = "", className = "" }) {
  const [bad, setBad] = useState(!src);
  if (bad) return <div className={"ph " + className} role="img" aria-label={alt} />;
  return <img src={src} alt={alt} className={className} loading="lazy" onError={() => setBad(true)} />;
}

export const money = (n) => "$" + Number(n).toFixed(2).replace(/\.00$/, "");
