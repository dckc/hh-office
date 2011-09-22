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

create index dab on hh_office.Client (id_dabble);
create index dab on hh_office.`Session` (id_dabble);
create index visit_match on hh_office.Visit (Session_id, Client_id);
create index visit_match on dabbledb.Visit (`session`, client);

select count(*)
from hh_office.Visit
where id_dabble is not null;

insert into hh_office.Visit (
  id_dabble, Session_id, Client_id, attend_n, charge, client_paid
, note, bill_date, check_date, insurance_paid)
select 0+dv.id as id_dabble, hs.id as Session_id, hc.id as Client_id
     , 0+attend as attend_n
     , 0+substr(dg.rate, length('USD $.')) as charge
     , 0+substr(`client pd`, length('USD $.')) as client_paid
     , dv.note
     , case when `bill date` > ''
       then STR_TO_DATE(`bill date`,'%m/%d/%Y')
       else null end as bill_date
     , case when `check date` > ''
       then STR_TO_DATE(`check date`,'%m/%d/%Y')
       else null end as check_date
     , case when `ins paid $` > ''
       then 0+substr(`ins paid $`, length('USD $.'))
       else null end as insurance_paid
from dabbledb.Visit dv
join dabbledb.`Session` ds on dv.session = ds.id
join dabbledb.`Group` dg on ds.group = dg.id
left join hh_office.Session hs on dv.session = hs.id_dabble
left join hh_office.Client hc on dv.client = hc.id_dabble
left join hh_office.Visit hv on hv.Session_id = hs.id and hv.Client_id = hc.id
where dv.session > '' and dv.client > ''
and hc.id is null or hs.id is null;
