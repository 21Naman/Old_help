"use client";

const TOKEN_KEY = "ally.token";

/** JWT sign-in is on when NEXT_PUBLIC_AUTH=jwt. Local dev without it uses a dev identity. */
export function authEnabled(): boolean {
  return process.env.NEXT_PUBLIC_AUTH === "jwt";
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    const token = window.localStorage.getItem(TOKEN_KEY);
    if (!token) return null;
    const exp = Number(claims(token).exp ?? 0);
    if (exp && exp * 1000 < Date.now()) {
      window.localStorage.removeItem(TOKEN_KEY);
      return null;
    }
    return token;
  } catch {
    return null;
  }
}

export function setToken(token: string | null): void {
  try {
    if (token) window.localStorage.setItem(TOKEN_KEY, token);
    else window.localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* storage unavailable */
  }
}

export async function idToken(): Promise<string | null> {
  if (!authEnabled()) return null;
  return getToken();
}

/** Reads the payload of a JWT without verifying it; the API does the verifying. */
function claims(token: string): Record<string, unknown> {
  try {
    const part = token.split(".")[1] ?? "";
    const b64 = part.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(part.length / 4) * 4, "=");
    const json = decodeURIComponent(
      Array.from(atob(b64), (c) => `%${c.charCodeAt(0).toString(16).padStart(2, "0")}`).join(""),
    );
    return JSON.parse(json) as Record<string, unknown>;
  } catch {
    return {};
  }
}

export interface Viewer {
  memberId: string;
  isParent: boolean;
  groups: string[];
}

export async function currentViewer(): Promise<Viewer> {
  if (!authEnabled()) {
    const dev = devMember();
    return { memberId: dev, isParent: dev === "parent", groups: [dev === "parent" ? "parent" : "family"] };
  }
  const payload = claims(getToken() ?? "");
  const groups = Array.isArray(payload.groups) ? payload.groups.map(String) : [];
  const isParent = groups.includes("parent");
  return {
    memberId: isParent ? "parent" : String(payload.member_id ?? payload.sub ?? ""),
    isParent,
    groups,
  };
}

export function devMember(): string {
  if (typeof window === "undefined") return "parent";
  try {
    return window.localStorage.getItem("ally.devMember") || "parent";
  } catch {
    return "parent";
  }
}

export function setDevMember(member: string): void {
  try {
    window.localStorage.setItem("ally.devMember", member);
  } catch {
    /* storage unavailable */
  }
}
