import { ClientRedirect } from "@/components/ClientRedirect";

/** The written landing is `/` in this app. Keep /classic so old world links still work. */
export default function ClassicRedirect() {
  return <ClientRedirect to="/" />;
}
