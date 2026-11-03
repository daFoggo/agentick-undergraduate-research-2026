import type { MetadataRoute } from "next"

/** The studio is an app behind sign-in: nothing here should be indexed (the landing page is apps/web). */
export default function robots(): MetadataRoute.Robots {
  return { rules: [{ userAgent: "*", disallow: "/" }] }
}
