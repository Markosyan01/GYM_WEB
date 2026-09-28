import { NavLink, Link, Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./auth";
import { useCart } from "./cart";
import { useLang, LANGS } from "./i18n";
import { Classes, Plans, SignIn, Account } from "./pages";
import { Home, Trainers, Shop, Cart, Gallery, Contact } from "./pages2";

export default function App() {
  const { user, signOut, ready } = useAuth();
  const { count } = useCart();
  const { t, lang, setLang } = useLang();
  if (!ready) return null;
  return (
    <>
      <header className="bar">
        <Link to="/" className="logo">Iron Yard</Link>
        <nav>
          <NavLink to="/classes">{t("Classes")}</NavLink>
          <NavLink to="/plans">{t("Plans")}</NavLink>
          <NavLink to="/trainers">{t("Trainers")}</NavLink>
          <NavLink to="/shop">{t("Shop")}</NavLink>
          <NavLink to="/gallery">{t("Gallery")}</NavLink>
          <NavLink to="/contact">{t("Contact")}</NavLink>
        </nav>
        <div className="who">
          <div className="lang" role="group" aria-label="Language">
            {LANGS.map(([code, label]) => (
              <button key={code} className={code === lang ? "on" : ""} aria-pressed={code === lang} onClick={() => setLang(code)}>{label}</button>
            ))}
          </div>
          <Link to="/cart" className="cartlink">{t("Cart")}{count > 0 ? ` (${count})` : ""}</Link>
          {user ? (<><Link to="/account">{user.name}</Link><button className="ghost" onClick={signOut}>{t("Sign out")}</button></>)
                : <Link className="btn" to="/signin">{t("Sign in")}</Link>}
        </div>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/classes" element={<Classes />} />
          <Route path="/plans" element={<Plans />} />
          <Route path="/trainers" element={<Trainers />} />
          <Route path="/shop" element={<Shop />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/gallery" element={<Gallery />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/signin" element={user ? <Navigate to="/account" /> : <SignIn />} />
          <Route path="/account" element={user ? <Account /> : <Navigate to="/signin" />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
      <footer>{t("Iron Yard Gym. Open 5am to 11pm, every day.")}</footer>
    </>
  );
}
