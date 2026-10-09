-- PataKeja database setup. Paste ALL of this into Supabase > SQL Editor > Run.

create table listings (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  approved_at timestamptz,
  expires_at timestamptz,
  status text not null default 'pending' check (status in ('pending','live','taken','rejected')),
  verified boolean not null default false,
  estate text not null,
  plot_name text not null,
  landmark text,
  category text not null,
  rent int not null check (rent > 0),
  deposit int,
  description text,
  amenities text[] not null default '{}',
  contact_name text,
  contact_role text,
  contact_phone text not null,
  lat double precision,
  lng double precision,
  pub_lat double precision,   -- approximate public pin (about 200 m off)
  pub_lng double precision,
  photos text[] not null default '{}',
  views int not null default 0,
  manage_code text,
  admin_notes text
);

create table reports (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  listing_id uuid references listings(id) on delete cascade,
  reason text not null,
  resolved boolean not null default false
);

-- Approximate public pin: shift exact location by up to ~200 m
create function set_public_pin() returns trigger language plpgsql as $$
begin
  if new.lat is not null and new.lng is not null then
    new.pub_lat := new.lat + (random() - 0.5) * 0.0036;
    new.pub_lng := new.lng + (random() - 0.5) * 0.0036;
  end if;
  return new;
end $$;
create trigger trg_pin before insert on listings for each row execute function set_public_pin();

alter table listings enable row level security;
alter table reports enable row level security;

-- Public can see only live, unexpired listings
create policy "public read live" on listings for select to anon, authenticated
  using (status = 'live' and expires_at > now());
-- Anyone can submit, but only as "pending"
create policy "public submit" on listings for insert to anon, authenticated
  with check (status = 'pending' and verified = false and approved_at is null and expires_at is null and views = 0);
-- Logged-in admin can do everything
create policy "admin all" on listings for all to authenticated using (true) with check (true);

create policy "public report" on reports for insert to anon, authenticated with check (resolved = false);
create policy "admin reports" on reports for all to authenticated using (true) with check (true);

-- Hide private columns (phone, exact location, owner code) from the public
revoke all on listings from anon;
revoke all on reports from anon;
grant insert on listings to anon;
grant insert on reports to anon;
grant select (id, created_at, approved_at, expires_at, status, verified, estate, plot_name, landmark,
              category, rent, deposit, description, amenities, photos, views, pub_lat, pub_lng)
  on listings to anon;

-- Contact details are handed out one listing at a time (this is where the KSh 100 unlock goes in Phase 2)
create function get_contact(p_id uuid)
returns table (contact_name text, contact_role text, contact_phone text, lat double precision, lng double precision)
language sql security definer set search_path = public as $$
  select contact_name, contact_role, contact_phone, lat, lng
  from listings where id = p_id and status = 'live' and expires_at > now();
$$;

create function bump_views(p_id uuid) returns void
language sql security definer set search_path = public as $$
  update listings set views = views + 1 where id = p_id and status = 'live';
$$;

-- Owner marks house as taken using the code shown after posting
create function mark_taken(p_id uuid, p_code text) returns boolean
language plpgsql security definer set search_path = public as $$
begin
  update listings set status = 'taken' where id = p_id and manage_code is not null and manage_code = p_code;
  return found;
end $$;

grant execute on function get_contact(uuid), bump_views(uuid), mark_taken(uuid, text) to anon, authenticated;

-- Photo storage
insert into storage.buckets (id, name, public) values ('photos', 'photos', true) on conflict do nothing;
create policy "anyone upload photos" on storage.objects for insert to anon, authenticated with check (bucket_id = 'photos');
create policy "public view photos" on storage.objects for select to anon, authenticated using (bucket_id = 'photos');
