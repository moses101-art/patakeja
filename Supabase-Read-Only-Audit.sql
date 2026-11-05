-- Run as a project administrator. Returns security metadata only.
-- Review grants and RLS for tables used by PataKeja.
select c.relname as table_name,
       c.relrowsecurity as rls_enabled,
       has_table_privilege('anon', c.oid, 'SELECT') as anon_table_read,
       has_table_privilege('authenticated', c.oid, 'SELECT') as signed_in_table_read,
       has_table_privilege('anon', c.oid, 'INSERT') as anon_insert,
       has_table_privilege('anon', c.oid, 'UPDATE') as anon_update,
       has_table_privilege('anon', c.oid, 'DELETE') as anon_delete
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'public' and c.relkind in ('r', 'p')
order by c.relname;

-- Review contact and homepage RPC definitions separately.
-- Share only after removing any embedded secrets.
-- select pg_get_functiondef(p.oid)
-- from pg_proc p join pg_namespace n on n.oid = p.pronamespace
-- where n.nspname = 'public' and p.proname in ('pk_homes','get_contact');
