-- Foundation: private helper schema, role helpers, profiles and the staff-role RPCs `packages/auth` expects.
-- Roles live in `app_metadata` (writable only through `set_staff_role`), never in `user_metadata`.

create schema if not exists private;
revoke all on schema private from public, anon, authenticated;
grant usage on schema private to anon, authenticated;

create or replace function private.jwt_role()
returns text
language sql
stable
set search_path = ''
as $$
  select coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '')
$$;

create or replace function private.is_staff()
returns boolean
language sql
stable
set search_path = ''
as $$
  select private.jwt_role() in ('editor', 'admin')
$$;

create or replace function private.is_admin()
returns boolean
language sql
stable
set search_path = ''
as $$
  select private.jwt_role() = 'admin'
$$;

create or replace function private.set_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

grant execute on function private.is_staff(), private.is_admin(), private.jwt_role() to anon, authenticated;

create table public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  full_name text check (full_name is null or length(full_name) <= 120),
  phone text check (phone is null or length(phone) <= 32),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create trigger profiles_updated_at before update on public.profiles
  for each row execute function private.set_updated_at();

create or replace function private.create_profile()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.profiles (id, full_name)
  values (new.id, nullif(left(new.raw_user_meta_data ->> 'name', 120), ''))
  on conflict (id) do nothing;
  return new;
end;
$$;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function private.create_profile();
revoke execute on function private.create_profile() from public, anon, authenticated;

revoke all on public.profiles from anon, authenticated;
alter table public.profiles enable row level security;
create policy "own profile or staff" on public.profiles for select to authenticated
  using (id = (select auth.uid()) or (select private.is_staff()));
create policy "own profile" on public.profiles for update to authenticated
  using (id = (select auth.uid())) with check (id = (select auth.uid()));
grant select, update (full_name, phone) on public.profiles to authenticated;

-- Admin-only: grant or remove a staff role. The change applies after the target's token refreshes.
create or replace function public.set_staff_role(target uuid, new_role text)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  if not private.is_admin() then
    raise exception 'forbidden' using errcode = '42501';
  end if;
  if new_role not in ('customer', 'editor', 'admin') then
    raise exception 'invalid_role' using errcode = 'P0001';
  end if;
  if target = auth.uid() and new_role <> 'admin' then
    raise exception 'cannot_demote_self' using errcode = 'P0001';
  end if;
  update auth.users
  set raw_app_meta_data = case
    when new_role = 'customer' then coalesce(raw_app_meta_data, '{}'::jsonb) - 'role'
    else coalesce(raw_app_meta_data, '{}'::jsonb) || jsonb_build_object('role', new_role)
  end
  where id = target;
  if not found then
    raise exception 'unknown_user' using errcode = 'P0001';
  end if;
end;
$$;

-- Admin-only: accounts with their role.
create or replace function public.list_accounts(search text default null)
returns table (id uuid, email text, full_name text, role text, created_at timestamptz, last_sign_in_at timestamptz)
language plpgsql
stable
security definer
set search_path = ''
as $$
begin
  if not private.is_admin() then
    raise exception 'forbidden' using errcode = '42501';
  end if;
  return query
  select u.id, u.email::text, p.full_name, coalesce(u.raw_app_meta_data ->> 'role', 'customer'), u.created_at,
    u.last_sign_in_at
  from auth.users u
  left join public.profiles p on p.id = u.id
  where search is null or u.email ilike '%' || search || '%' or p.full_name ilike '%' || search || '%'
  order by (u.raw_app_meta_data ->> 'role') is null, u.created_at desc
  limit 200;
end;
$$;

-- Supabase grants EXECUTE on new public functions to anon directly; keep these signed-in only.
revoke execute on function public.set_staff_role(uuid, text), public.list_accounts(text) from public, anon;
grant execute on function public.set_staff_role(uuid, text), public.list_accounts(text) to authenticated;
alter default privileges in schema public revoke execute on functions from anon;
