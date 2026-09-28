import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "./api";
import { useAuth } from "./auth";
import { useCart } from "./cart";
import { useLang } from "./i18n";
import { Img, money } from "./ui";

const todayKey = () => ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][new Date().getDay()];
const useFetch = (path, init = []) => {
  const [d, setD] = useState(init);
  useEffect(() => { api(path).then(setD).catch(() => {}); }, [path]);
  return d;
};
const left = (c) => c.capacity - c.booked;

export function Home() {
  const { t } = useLang();
  const classes = useFetch("/classes");
  const facilities = useFetch("/facilities");
  const quotes = useFetch("/testimonials");
  const products = useFetch("/products");
  const today = classes.filter((c) => c.day === todayKey());
  return (
    <>
      <section className="hero-photo">
        <Img src="/images/hero.svg" alt="" className="bg" />
        <div className="hero-copy">
          <h1>{t("Lift heavy.")}<br />{t("Show up often.")}</h1>
          <p>{t("A no-frills gym with real barbells, coached classes and people who know your name.")}</p>
          <div className="row"><Link className="btn" to="/plans">{t("See plans")}</Link><Link className="ghost-link" to="/classes">{t("Browse classes")}</Link></div>
        </div>
      </section>

      <section className="board">
        <h2>{t("On the floor today")} ({t(todayKey())})</h2>
        {today.length === 0 ? <p className="muted">{t("No classes today. The floor is open all day.")}</p> : (
          <ul className="rows">
            {today.map((c) => (
              <li key={c.id}><b className="time">{c.start}</b><span>{t(c.title)}<small>{t("with {name}", { name: t(c.trainer) })}</small></span>
                <em className={left(c) === 0 ? "full" : ""}>{left(c) === 0 ? t("Full") : t("Spots left: {n}", { n: left(c) })}</em></li>
            ))}
          </ul>
        )}
      </section>

      <section className="block">
        <h2>{t("The facilities")}</h2>
        <div className="cards">
          {facilities.map((f) => (
            <article key={f.id} className="card"><Img src={f.image} alt={t(f.name)} /><div><h3>{t(f.name)}</h3><p>{t(f.description)}</p></div></article>
          ))}
        </div>
      </section>

      <section className="block">
        <h2>{t("Popular classes")}</h2>
        <div className="cards">
          {classes.slice(0, 4).map((c) => (
            <article key={c.id} className="card"><Img src={c.image} alt={t(c.title)} /><div><h3>{t(c.title)}</h3><p>{t(c.day)} {c.start} · {t("with {name}", { name: t(c.trainer) })}</p></div></article>
          ))}
        </div>
      </section>

      <section className="block">
        <div className="head"><h2>{t("From the shop")}</h2><Link to="/shop">{t("Visit the shop")}</Link></div>
        <div className="cards four">
          {products.slice(0, 4).map((p) => (
            <article key={p.id} className="card"><Img src={p.image} alt={t(p.name)} /><div><h3>{t(p.name)}</h3><p>{money(p.price)}</p></div></article>
          ))}
        </div>
      </section>

      <section className="block">
        <h2>{t("What members say")}</h2>
        <div className="cards">
          {quotes.map((q) => (
            <figure key={q.id} className="quote"><blockquote>{t(q.quote)}</blockquote>
              <figcaption><Img src={q.image} alt="" className="avatar" /><span>{t(q.name)}<small>{t(q.detail)}</small></span></figcaption></figure>
          ))}
        </div>
      </section>
    </>
  );
}

export function Trainers() {
  const { t } = useLang();
  const list = useFetch("/trainers");
  return (
    <section>
      <h1>{t("Trainers")}</h1>
      <div className="cards">
        {list.map((tr) => (
          <article key={tr.id} className="card tall"><Img src={tr.image} alt={t(tr.name)} /><div><h2>{t(tr.name)}</h2><h3>{t(tr.specialty)}</h3><p>{t(tr.bio)}</p></div></article>
        ))}
      </div>
    </section>
  );
}

export function Shop() {
  const { t } = useLang();
  const [cat, setCat] = useState("");
  const all = useFetch("/products");
  const { add } = useCart();
  const [added, setAdded] = useState(null);
  const cats = ["", ...new Set(all.map((p) => p.category))];
  const list = cat ? all.filter((p) => p.category === cat) : all;
  return (
    <section>
      <h1>{t("Shop")}</h1>
      <div className="tabs">{cats.map((c) => <button key={c} className={c === cat ? "on" : ""} onClick={() => setCat(c)}>{c ? t(c) : t("All")}</button>)}</div>
      <div className="cards four">
        {list.map((p) => (
          <article key={p.id} className="card">
            <Img src={p.image} alt={t(p.name)} />
            <div><h3>{t(p.name)}</h3><p>{t(p.description)}</p>
              <p className="price-row"><b>{money(p.price)}</b>
                <button className="btn" disabled={p.stock === 0} onClick={() => { add(p); setAdded(p.id); }}>
                  {p.stock === 0 ? t("Sold out") : added === p.id ? t("Added") : t("Add to cart")}
                </button></p></div>
          </article>
        ))}
      </div>
    </section>
  );
}

export function Cart() {
  const { t } = useLang();
  const { lines, setQty, clear, total } = useCart();
  const { user } = useAuth();
  const nav = useNavigate();
  const [msg, setMsg] = useState("");
  const [done, setDone] = useState(null);
  const orders = useFetch(user ? "/me/orders" : "/products?category=__none__", []);
  const checkout = async () => {
    if (!user) return nav("/signin");
    setMsg("");
    try {
      const o = await api("/orders", { method: "POST", body: { items: lines.map((l) => ({ product_id: l.id, qty: l.qty })) } });
      clear(); setDone(o);
    } catch (e) { setMsg(e.message); }
  };
  return (
    <section>
      <h1>{t("Cart")}</h1>
      {done && <p className="ok" role="status">{t("Order #{id} placed. Total {total}. Pay and collect at the front desk.", { id: done.id, total: money(done.total) })}</p>}
      {lines.length === 0 ? <p className="muted">{t("Your cart is empty.")} <Link to="/shop">{t("Go to the shop")}</Link></p> : (
        <>
          <ul className="rows cart">
            {lines.map((l) => (
              <li key={l.id}><Img src={l.image} alt="" className="thumb sq" /><span>{t(l.name)}<small>{t("{price} each", { price: money(l.price) })}</small></span>
                <span className="qty"><button className="ghost" aria-label={t("Fewer") + " " + t(l.name)} onClick={() => setQty(l.id, l.qty - 1)}>-</button><b>{l.qty}</b>
                  <button className="ghost" aria-label={t("More") + " " + t(l.name)} onClick={() => setQty(l.id, l.qty + 1)}>+</button></span>
                <b>{money(l.price * l.qty)}</b></li>
            ))}
          </ul>
          <p className="total">{t("Total")} <b>{money(total)}</b></p>
          {msg && <p className="err" role="alert">{t(msg)}</p>}
          <button className="btn" onClick={checkout}>{user ? t("Place order") : t("Sign in to order")}</button>
        </>
      )}
      {user && orders.length > 0 && orders[0].lines && (<><h2>{t("Past orders")}</h2>
        <ul className="rows">{orders.map((o) => <li key={o.id}><b className="time">#{o.id}</b><span>{o.lines.join(", ")}</span><b>{money(o.total)}</b></li>)}</ul></>)}
    </section>
  );
}

const GALLERY = ["barbell", "glove", "yoga", "kettlebell", "cardio", "hiit", "rig", "sauna", "dumbbell", "studio", "locker", "person1"];

export function Gallery() {
  const { t } = useLang();
  const [open, setOpen] = useState(null);
  return (
    <section>
      <h1>{t("Gallery")}</h1>
      <div className="masonry">
        {GALLERY.map((tag, i) => (
          <button key={tag} className="shot" onClick={() => setOpen(i)} aria-label={t("Open photo {n}", { n: i + 1 })}>
            <Img src={`/images/${tag}.svg`} alt={tag} />
          </button>
        ))}
      </div>
      {open !== null && (
        <div className="lightbox" role="dialog" aria-modal="true" onClick={() => setOpen(null)}>
          <Img src={`/images/${GALLERY[open]}.svg`} alt={GALLERY[open]} />
          <button className="ghost" onClick={() => setOpen(null)}>{t("Close")}</button>
        </div>
      )}
    </section>
  );
}

const FAQ = [
  ["Do I need experience?", "No. Every class has beginner options and coaches show you how to scale."],
  ["Can I freeze my membership?", "Yes, for up to 2 months a year. Ask at the front desk."],
  ["Is there a joining fee?", "No. Plans are monthly and you can cancel any time."],
  ["What should I bring?", "Trainers, a towel and water. We provide chalk, straps and gloves."],
];

export function Contact() {
  const { t } = useLang();
  const [f, setF] = useState({ name: "", email: "", body: "" });
  const [state, setState] = useState("");
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const send = async (e) => {
    e.preventDefault(); setState("");
    try { await api("/contact", { method: "POST", body: f }); setState("sent"); setF({ name: "", email: "", body: "" }); }
    catch (x) { setState(x.message); }
  };
  return (
    <section className="two">
      <div>
        <h1>{t("Contact")}</h1>
        <p>{t("Open 5am to 11pm, every day.")}</p>
        <form onSubmit={send}>
          <label>{t("Name")}<input required value={f.name} onChange={set("name")} /></label>
          <label>{t("Email")}<input required type="email" value={f.email} onChange={set("email")} /></label>
          <label>{t("Message")}<textarea required minLength={5} rows={5} value={f.body} onChange={set("body")} /></label>
          {state === "sent" && <p className="ok" role="status">{t("Message sent. We reply within one working day.")}</p>}
          {state && state !== "sent" && <p className="err" role="alert">{t(state)}</p>}
          <button className="btn">{t("Send message")}</button>
        </form>
      </div>
      <div>
        <h2>{t("Questions people ask")}</h2>
        {FAQ.map(([q, a]) => <details key={q}><summary>{t(q)}</summary><p>{t(a)}</p></details>)}
      </div>
    </section>
  );
}
