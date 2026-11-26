import { ClientRedirect } from "@/components/ClientRedirect";

/** Legacy link — the family experience now lives on /home. */
export default function FamilyIndexRedirect() {
  return <ClientRedirect to="/home" />;
}
