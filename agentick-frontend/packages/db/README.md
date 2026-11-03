# @workspace/db

Supabase clients, errors, generated types and the `supabase/` CLI directory shared by `apps/web` and `apps/admin`.

| Script (`pnpm --filter @workspace/db …`) | What it does |
| :--- | :--- |
| `exec supabase migration new <name>` | New migration in `supabase/migrations` (never hand-name the file) |
| `db:test -- --dry` | Runs every pgTAP file with all migrations prepended, inside one transaction that rolls back: try unpushed migrations without touching the database |
| `db:push` | Applies new migrations to the linked project |
| `db:test` | Runs the pgTAP files against the linked project (each rolls back) |
| `db:types` | Regenerates `src/database.types.ts`; run after every pushed migration |
| `exec supabase db advisors --linked` | Security and performance lints |

`supabase test db --linked` needs Docker for `pg_prove`; `scripts/test-db.mjs` runs the same files through
`supabase db query` instead. Each test file is `begin; … rollback;`, collects TAP lines in a temp table `tap_out`
and ends by selecting them as one `tap` column, because the Management API returns only the last result set.

The foundation migration (`supabase/migrations/20261026000001_foundation.sql`) holds what `@workspace/auth` needs:
role helpers read from `app_metadata`, `profiles` with RLS, and the admin-only `set_staff_role` / `list_accounts`
RPCs. Add your own tables in new migrations. `signing_keys.json` is local-only and git-ignored.
