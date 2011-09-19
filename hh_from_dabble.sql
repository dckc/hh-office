/** hh_from_dabble.sql -- restore from CSV data
 */

-- insert into hh_office.Office
/*
select null, name, fax, address, notes, 0+id as id_dabble
from dabbledb.Office
where name > '';

select *
from dabbledb.Office
where id not in (
select id_dabble from zc.zcfrm_office);
*/

-- these look like they were cleaned up; do we want them?
select *
from dabbledb.Officer do
left join hh_office.Officer ho on ho.id_dabble = do.id
where ho.id_dabble is null;


-- never mind batches

select *
from dabbledb.Client dc
left join hh_office.Client hc on hc.id_dabble = dc.id
where hc.id_dabble is null;

/* 
insert into clients
select 0+id, name, ins, approval, dx, note
     , case when officer > ''
       then 0+officer else null end
     , dob, address, phone
     , case when batch > ''
       then 0+batch else null end
from Client;
*/


-- just one stray group
select *
from dabbledb.`Group` dg
left join hh_office.`Group` hg on hg.id_dabble = dg.id
where hg.id_dabble is null;

create index gid on dabbledb.`Group` (id);
create index session_dabble on hh_office.`Session` (id_dabble);

insert into hh_office.`Session`
 (session_date, time, Group_id, Therapist_id, id_dabble)
select STR_TO_DATE(ds.`date`,'%m/%d/%Y'), ds.time, hg.id, ht.id, ds.id
 from dabbledb.`Session` ds
 join dabbledb.`Group` dg on ds.`group` = dg.id
 join hh_office.`Group` hg on hg.id_dabble = dg.id
 join hh_office.Therapist ht on ht.name = ds.Therapist
 left join hh_office.`Session` hs on hs.id_dabble = ds.id
where hs.id_dabble is null;


create index visit_id on dabbledb.`Visit` (id);
create index visit_dabble on hh_office.`Visit` (id_dabble);

-- ouch!!!
select count(*)
from zc.zcfrm_visit
where id_dabble is not null;

select *
from hh_office.Attendance a
join (
select count(*), Session_id, Client_id
from hh_office.Visit
group by Session_id, Client_id
having count(*) > 1
) dups on dups.Client_id = a.client_id and dups.Session_id = a.session_id;

/********* **********/

select count(*)
from hh_office.Visit
where id_dabble is not null;

select count(*)
from dabbledb.Visit dv
left join hh_office.Visit hv on hv.id_dabble = dv.id
where hv.id_dabble is null;


insert into visits
select 0+id, 0+session, 0+client
     , case when attend > 0 then 'true' else 'false' end
     , 0+substr(client_pd, length('USD $.'))
     , note
     , case when bill_date > '' then
       substr(bill_date, 7, 4) || '-' ||
       substr(bill_date, 1, 2) || '-' ||
       substr(bill_date, 4, 2)
       else null end
     , case when check_date > '' then
       substr(check_date, 7, 4) || '-' ||
       substr(check_date, 1, 2) || '-' ||
       substr(check_date, 4, 2)
       else null end
     , case when "INS_PAID_$" > ''
       then 0+substr("INS_PAID_$", length('USD $.'))
       else null end
from Visit
where session > '' and client > '';

create table current_clients as
select c.* from clients c
join (
  select max(s.date) last_seen, c.id
  from clients c
  join visits v on v.client = c.id
  join sessions s on v.session = s.id
  group by c.id
  ) t
on t.id == c.id
where julianday('2011-05-18') - julianday(t.last_seen) < 60
;

create table current_visits as
select v.*
from visits v
join current_clients cc
  on v.client = cc.id
;

create table current_sessions as
select s.*
from sessions s
join (select distinct session from current_visits) v
  on v.session = s.id
;
