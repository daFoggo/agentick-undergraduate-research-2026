import { createClient } from "@supabase/supabase-js"

import type { Database } from "./database.types"
import { supabaseEnv } from "./env"

/**
 * Anonymous client: no cookies and no session, so it is safe inside `"use cache"`. RLS limits it to
 * what the public may read (published rows).
 */
export function createPublicClient() {
  return createClient<Database>(supabaseEnv.url, supabaseEnv.publishableKey, {
    auth: { persistSession: false, autoRefreshToken: false },
  })
}
