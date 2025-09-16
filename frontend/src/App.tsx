import React, { useEffect, useState } from "react";
import { useAppDispatch, useAppSelector } from "./hooks";
import { login, logout, refresh } from "./store/authSlice";
import api from "./api/axios";

export default function App() {
  const dispatch = useAppDispatch();
  const { access, user, status } = useAppSelector(s => s.auth);
  const [me, setMe] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);

  // Rehydrate on app load (uses HttpOnly refresh cookie)
  useEffect(() => { dispatch(refresh()); }, [dispatch]);

  const onLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const f = e.target as HTMLFormElement;
    await dispatch(login({
      username: (f.elements.namedItem("username") as HTMLInputElement).value,
      password: (f.elements.namedItem("password") as HTMLInputElement).value,
    }));
  };

  const callMe = async () => {
    try { const { data } = await api.get("/me/"); setMe(data); setErr(null); }
    catch (e: any) { setErr(e?.response?.data?.detail || "error"); }
  };

  return (
    <div style={{ padding: 24, fontFamily: "system-ui", maxWidth: 560 }}>
      <h2>React + Django JWT</h2>
      <p style={{ opacity: 0.75 }}>Access in memory; refresh in HttpOnly cookie.</p>

      {!access ? (
        <form onSubmit={onLogin} style={{ display: "grid", gap: 8, maxWidth: 320 }}>
          <input name="username" placeholder="username" />
          <input name="password" type="password" placeholder="password" />
          <button disabled={status==="loading"}>{status==="loading"?"…":"Login"}</button>
        </form>
      ) : (
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <div>Signed in as <b>{user?.username}</b></div>
          <button onClick={()=>dispatch(logout())}>Logout</button>
        </div>
      )}

      <hr style={{ margin: "16px 0" }} />
      <button onClick={callMe}>Call /api/me (protected)</button>
      {me && <pre>{JSON.stringify(me, null, 2)}</pre>}
      {err && <div style={{ color:"crimson" }}>{err}</div>}
    </div>
  );
}
