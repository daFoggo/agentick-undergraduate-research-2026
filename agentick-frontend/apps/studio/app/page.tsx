import { redirect } from "next/navigation"

import { DASHBOARD_PATH } from "@/config/routes"

/** The studio has no public home: the landing page is apps/web. `proxy.ts` sends a signed-out visitor on to sign-in. */
export default function HomePage() {
  redirect(DASHBOARD_PATH)
}
