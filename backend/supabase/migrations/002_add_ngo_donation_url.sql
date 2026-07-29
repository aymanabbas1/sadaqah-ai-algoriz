alter table public.ngos add column if not exists donation_url text;

update public.ngos
set donation_url = case id
  when 'care' then 'https://www.care.org/get-involved/ways-to-give/'
  when 'human-appeal' then 'https://humanappeal.org.uk/donate'
  when 'islamic-relief' then 'https://islamic-relief.org/ways-to-donate/'
  when 'mercy-corps' then 'https://www.mercycorps.org/donate'
  when 'save-the-children' then 'https://www.savethechildren.net/about-us/how-you-can-help'
  else donation_url
end
where donation_url is null;

alter table public.ngos alter column donation_url set not null;
