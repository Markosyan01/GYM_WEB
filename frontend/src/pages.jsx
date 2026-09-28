import { useEffect, useState, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "./api";
import { useAuth } from "./auth";
import { useLang } from "./i18n";
import { Img } from "./ui";

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const todayKey = () => ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][new Date().getDay()];
const left = (c) => c.capacity - c.booked;

function useClasses() {
  const [items, setItems] = useState([]);
  const load = useCallback(() => api("/classes").then(setItems).catch(() => {}), []);
  useEffect(() => { load(); }, [load]);
  return [items, load];
}

export function Classes() {
  const { user } = useAuth();
  const { t } = useLang();
  const nav = useNavigate();
  const [items, load] = useClasses();
  const [day, setDay] = useState(todayKey());
  const [msg, setMsg] = useState("");

  const act = async (c) => {
    if (!user) return nav("/signin");
    setMsg("");
    try { await api(`/classes/${c.id}/book`, { method: c.joined ? "DELETE" : "POST" }); await load(); }
    catch (e) { setMsg(e.message); }
  };
  const list = items.filter((c) => c.day === day);
  return (
    <section>
      <h1>{t("Classes")}</h1>
      <div className="tabs">{DAYS.map((d) => <button key={d} className={d === day ? "on" : ""} onClick={() => setDay(d)}>{t(d)}</button>)}</div>
      {msg && <p className="err" role="alert">{t(msg)} {msg.includes("plan") && <Link to="/plans">{t("See plans.")}</Link>}</p>}
      {list.length === 0 && <p className="muted">{t("No classes on {day}.", { day: t(day) })}</p>}
      <ul className="rows big">
        {list.map((c) => (
          <li key={c.id}>
            <Img src={c.image} alt="" className="thumb" />
            <span><b className="time">{c.start}</b> {t(c.title)}<small>{t(c.description)} {t("with {name}", { name: t(c.trainer) })}</small></span>
            <em className={left(c) === 0 ? "full" : ""}>{t("{a} of {b} left", { a: left(c), b: c.capacity })}</em>
            <button className={c.joined ? "ghost" : "btn"} disabled={!c.joined && left(c) === 0} onClick={() => act(c)}>
              {c.joined ? t("Cancel booking") : left(c) === 0 ? t("Full") : t("Book class")}
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}

export function Plans() {
  const { user, refresh } = useAuth();
  const { t } = useLang();
  const nav = useNavigate();
  const [plans, setPlans] = useState([]);
  const [msg, setMsg] = useState("");
  useEffect(() => { api("/plans").then(setPlans).catch(() => {}); }, []);
  const choose = async (p) => {
    if (!user) return nav("/signin");
    try { await api(`/me/plan/${p.id}`, { method: "POST" }); await refresh(); setMsg(p.id); }
    catch (e) { setMsg(""); }
  };
  const chosen = plans.find((p) => p.id === msg);
  return (
    <section>
      <h1>{t("Membership plans")}</h1>
      <p className="muted">{t("Monthly, cancel any time.")}</p>
      {chosen && <p className="ok" role="status">{t("You are on the {name} plan.", { name: t(chosen.name) })}</p>}
      <div className="plans">
        {plans.map((p, i) => (
          <article key={p.id} className={i === 1 ? "plan pick" : "plan"}>
            <h2>{t(p.name)}</h2>
            <p className="price">${p.price}<span>{t("/month")}</span></p>
            <ul>{p.features.map((f) => <li key={f}>{t(f)}</li>)}</ul>
            <button className={user?.plan?.id === p.id ? "ghost" : "btn"} disabled={user?.plan?.id === p.id} onClick={() => choose(p)}>
              {user?.plan?.id === p.id ? t("Current plan") : t("Choose {name}", { name: t(p.name) })}
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}

export function SignIn() {
  const { sign } = useAuth();
  const { t } = useLang();
  const nav = useNavigate();
  const [mode, setMode] = useState("login");
  const [f, setF] = useState({ name: "", email: "", password: "" });
  const [err, setErr] = useState("");
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const submit = async (e) => {
    e.preventDefault(); setErr("");
    try { await sign(mode, mode === "login" ? { email: f.email, password: f.password } : f); nav("/account"); }
    catch (x) { setErr(x.message); }
  };
  return (
    <section className="narrow">
      <h1>{mode === "login" ? t("Sign in") : t("Create your account")}</h1>
      <form onSubmit={submit}>
        {mode === "register" && <label>{t("Name")}<input required value={f.name} onChange={set("name")} autoComplete="name" /></label>}
        <label>{t("Email")}<input required type="email" value={f.email} onChange={set("email")} autoComplete="email" /></label>
        <label>{t("Password")}<input required type="password" minLength={8} value={f.password} onChange={set("password")}
          autoComplete={mode === "login" ? "current-password" : "new-password"} /></label>
        {mode === "register" && <small className="muted">{t("At least 8 characters.")}</small>}
        {err && <p className="err" role="alert">{t(err)}</p>}
        <button className="btn">{mode === "login" ? t("Sign in") : t("Create account")}</button>
      </form>
      <button className="ghost-link" onClick={() => { setMode(mode === "login" ? "register" : "login"); setErr(""); }}>
        {mode === "login" ? t("New here? Create an account") : t("Have an account? Sign in")}
      </button>
    </section>
  );
}

export function Account() {
  const { user } = useAuth();
  const { t } = useLang();
  const [mine, setMine] = useState([]);
  const load = useCallback(() => api("/me/bookings").then(setMine).catch(() => {}), []);
  useEffect(() => { load(); }, [load]);
  const cancel = async (c) => { await api(`/classes/${c.id}/book`, { method: "DELETE" }); load(); };
  const order = (a, b) => DAYS.indexOf(a.day) - DAYS.indexOf(b.day) || a.start.localeCompare(b.start);
  return (
    <section>
      <h1>{t("Hi, {name}", { name: user.name })}</h1>
      <p>{user.plan ? <>{t("Your plan:")} <b>{t(user.plan.name)}</b> (${user.plan.price}{t("/month")})</> : <>{t("You have no plan yet.")} <Link to="/plans">{t("Choose a plan")}</Link></>}</p>
      <h2>{t("Your booked classes")}</h2>
      {mine.length === 0 ? <p className="muted">{t("Nothing booked.")} <Link to="/classes">{t("Browse classes")}</Link></p> : (
        <ul className="rows big">
          {[...mine].sort(order).map((c) => (
            <li key={c.id}><Img src={c.image} alt="" className="thumb" /><span><b className="time">{t(c.day)} {c.start}</b> {t(c.title)}<small>{t("with {name}", { name: t(c.trainer) })}</small></span><span />
              <button className="ghost" onClick={() => cancel(c)}>{t("Cancel booking")}</button></li>
          ))}
        </ul>
      )}
    </section>
  );
}
