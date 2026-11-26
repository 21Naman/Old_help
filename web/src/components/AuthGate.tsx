"use client";

import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { ShieldGlyph, BrandMark } from "@/components/landing/BrandMark";
import { authEnabled, currentViewer, devMember, getToken, setDevMember, setToken, type Viewer } from "@/lib/session";
import { surakshaApiUrl } from "@/lib/surakshaTypes";

function AuthHeader() {
  return (
    <div className="auth-brand">
      <BrandMark />
      <p className="eyebrow">Family sign in</p>
    </div>
  );
}

function BootScreen() {
  return (
    <div className="flex min-h-dvh items-center justify-center bg-paper">
      <span className="text-alert">
        <ShieldGlyph size={36} />
      </span>
    </div>
  );
}

/**
 * Signs the viewer in with a username and password (family phones, Amma's tablet). With
 * NEXT_PUBLIC_AUTH unset (local dev) it shows a small identity switcher instead.
 */
export function AuthGate({ children }: { children: (viewer: Viewer, signOut?: () => void) => ReactNode }) {
  if (!authEnabled()) return <DevGate>{children}</DevGate>;
  return <JwtGate>{children}</JwtGate>;
}

function JwtGate({ children }: { children: (viewer: Viewer, signOut?: () => void) => ReactNode }) {
  const [token, setTokenState] = useState<string | null | undefined>(undefined);
  useEffect(() => setTokenState(getToken()), []);
  if (token === undefined) return <BootScreen />;
  if (!token) return <LoginForm onToken={setTokenState} />;
  const signOut = () => {
    setToken(null);
    setTokenState(null);
  };
  return (
    <>
      <button
        type="button"
        onClick={signOut}
        className="fixed bottom-4 right-4 z-50 rounded-full border border-line bg-card/90 px-3.5 py-2 text-xs font-semibold text-ink-soft shadow-[0_8px_24px_-14px_oklch(0.26_0.032_42/0.5)] backdrop-blur hover:text-ink"
      >
        Sign out
      </button>
      <ViewerLoader key={token} signOut={signOut}>
        {children}
      </ViewerLoader>
    </>
  );
}

function LoginForm({ onToken }: { onToken: (token: string) => void }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(`${surakshaApiUrl()}/ally/auth/login`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ username: username.trim(), password }),
      });
      const body = (await res.json().catch(() => ({}))) as { token?: string; message?: string };
      if (!res.ok || !body.token) {
        setError(res.status === 401 ? "That username or password didn't match." : body.message ?? "Could not sign in.");
        return;
      }
      setToken(body.token);
      onToken(body.token);
    } catch {
      setError("Can't reach Suraksha. Check your connection.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex min-h-dvh items-center justify-center bg-paper px-4">
      <form onSubmit={(e) => void submit(e)} className="panel flex w-full max-w-sm flex-col gap-3 p-6">
        <AuthHeader />
        <input
          className="field"
          autoComplete="username"
          autoCapitalize="none"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          className="field"
          type="password"
          autoComplete="current-password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && <p className="m-0 text-sm text-alert">{error}</p>}
        <button type="submit" disabled={busy} className="btn btn-primary btn-block">
          {busy ? "Signing in…" : "Sign in"}
        </button>
      </form>
    </div>
  );
}

function ViewerLoader({
  children,
  signOut,
}: {
  children: (viewer: Viewer, signOut?: () => void) => ReactNode;
  signOut?: () => void;
}) {
  const [viewer, setViewer] = useState<Viewer | null>(null);
  useEffect(() => {
    void currentViewer().then(setViewer);
  }, []);
  if (!viewer) return <BootScreen />;
  return <>{children(viewer, signOut)}</>;
}

function DevGate({ children }: { children: (viewer: Viewer) => ReactNode }) {
  const [member, setMember] = useState<string | null>(null);
  useEffect(() => setMember(devMember()), []);
  if (!member) return <BootScreen />;
  const viewer: Viewer = { memberId: member, isParent: member === "parent", groups: [member === "parent" ? "parent" : "family"] };
  return (
    <>
      <div className="fixed bottom-4 right-4 z-50 flex items-center gap-2 rounded-full border border-line bg-card/90 px-3.5 py-2 text-xs text-ink-soft shadow-[0_8px_24px_-14px_oklch(0.26_0.032_42/0.5)] backdrop-blur">
        <span className="eyebrow-sm text-ink-faint">viewing as</span>
        <select
          className="cursor-pointer bg-transparent font-semibold text-ink outline-none"
          value={member}
          onChange={(e) => {
            setDevMember(e.target.value);
            window.location.reload();
          }}
        >
          <option value="parent">Amma (tablet)</option>
          <option value="rahul">Rahul</option>
          <option value="priya">Priya</option>
          <option value="sunita">Sunita aunty</option>
        </select>
      </div>
      {children(viewer)}
    </>
  );
}
