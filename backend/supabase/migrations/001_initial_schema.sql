create extension if not exists pgcrypto;

create table if not exists public.crises (
  id text primary key,
  name text not null,
  country text not null,
  iso3 text not null,
  lat double precision not null,
  lng double precision not null,
  crisis_type text not null,
  people_in_need text not null,
  people_in_need_value bigint,
  displaced_people text not null,
  displaced_people_value bigint,
  funding_status text not null,
  funding_requirement_usd numeric,
  response_plan_id bigint,
  response_plan_year integer,
  focus_areas text[] not null default '{}',
  affected_locations text[] not null default '{}',
  summary text not null,
  data_as_of timestamptz not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.ngos (
  id text primary key,
  initials text not null,
  short_name text not null,
  name text not null,
  descriptor text not null,
  coverage text not null,
  founded_year integer not null,
  reporting_year integer not null,
  annual_income text,
  annual_expenditure text,
  reported_reach text not null,
  countries_active integer not null,
  reported_activity text,
  donation_url text not null,
  accent text not null,
  accepted_giving_types text[] not null default '{}',
  focus_areas text[] not null default '{}',
  data_as_of timestamptz not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.ngo_crises (
  ngo_id text not null references public.ngos(id) on delete cascade,
  crisis_id text not null references public.crises(id) on delete cascade,
  evidence_url text not null,
  verified_at timestamptz not null,
  primary key (ngo_id, crisis_id)
);

create table if not exists public.sources (
  id uuid primary key default gen_random_uuid(),
  entity_type text not null check (entity_type in ('crisis', 'ngo')),
  entity_id text not null,
  title text not null,
  organization text not null,
  source_type text not null,
  url text not null,
  reporting_year integer,
  retrieved_at timestamptz,
  http_status integer,
  content_hash text,
  etag text,
  last_modified text,
  raw_excerpt text,
  last_error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (entity_type, entity_id, url)
);

create table if not exists public.ingestion_runs (
  id uuid primary key default gen_random_uuid(),
  status text not null check (status in ('running', 'completed', 'partial', 'failed')),
  trigger text not null default 'manual',
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  sources_checked integer not null default 0,
  sources_updated integer not null default 0,
  crises_updated integer not null default 0,
  ngos_updated integer not null default 0,
  errors jsonb not null default '[]'::jsonb
);

create index if not exists sources_entity_idx on public.sources(entity_type, entity_id);
create index if not exists ngo_crises_crisis_idx on public.ngo_crises(crisis_id);
create index if not exists ingestion_runs_started_idx on public.ingestion_runs(started_at desc);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists crises_set_updated_at on public.crises;
create trigger crises_set_updated_at before update on public.crises
for each row execute function public.set_updated_at();

drop trigger if exists ngos_set_updated_at on public.ngos;
create trigger ngos_set_updated_at before update on public.ngos
for each row execute function public.set_updated_at();

drop trigger if exists sources_set_updated_at on public.sources;
create trigger sources_set_updated_at before update on public.sources
for each row execute function public.set_updated_at();

alter table public.crises enable row level security;
alter table public.ngos enable row level security;
alter table public.ngo_crises enable row level security;
alter table public.sources enable row level security;
alter table public.ingestion_runs enable row level security;

drop policy if exists "Public crisis profiles are readable" on public.crises;
create policy "Public crisis profiles are readable" on public.crises
for select to anon, authenticated using (true);

drop policy if exists "Public NGO profiles are readable" on public.ngos;
create policy "Public NGO profiles are readable" on public.ngos
for select to anon, authenticated using (true);

drop policy if exists "Public NGO crisis links are readable" on public.ngo_crises;
create policy "Public NGO crisis links are readable" on public.ngo_crises
for select to anon, authenticated using (true);

drop policy if exists "Public sources are readable" on public.sources;
create policy "Public sources are readable" on public.sources
for select to anon, authenticated using (true);

revoke all on public.ingestion_runs from anon, authenticated;
revoke insert, update, delete on public.crises from anon, authenticated;
revoke insert, update, delete on public.ngos from anon, authenticated;
revoke insert, update, delete on public.ngo_crises from anon, authenticated;
revoke insert, update, delete on public.sources from anon, authenticated;
