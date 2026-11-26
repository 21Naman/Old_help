"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

/** Static export has no server redirects; old paths forward on the client instead. */
export function ClientRedirect({ to }: { to: string }) {
  const router = useRouter();
  useEffect(() => router.replace(to), [router, to]);
  return null;
}
