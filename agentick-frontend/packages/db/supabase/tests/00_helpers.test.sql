-- Smoke test for the foundation migration.
begin;
create extension if not exists pgtap with schema extensions;
create temp table tap_out (n serial, line text);
insert into tap_out (line) select plan(4);
insert into tap_out (line) select has_schema('private');
insert into tap_out (line) select has_function('private', 'is_staff', array[]::text[]);
insert into tap_out (line) select has_table('public', 'profiles', 'profiles exists');
insert into tap_out (line) select has_function('public', 'set_staff_role', array['uuid', 'text']);
insert into tap_out (line) select * from finish();
select string_agg(line, E'
' order by n) as tap from tap_out;
rollback;
