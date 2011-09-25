/** hh_from_dabble.sql -- restore from CSV data
 */

-- insert into hh_office.Office
/* Any missing offices? Just 4, and I think they're junk:

select *
from dabbledb.Office do
left join hh_office.Office ho on ho.id_dabble = do.id
where ho.id is null;

so don't bother...

select null, name, fax, address, notes, 0+id as id_dabble
from dabbledb.Office
where name > '';
*/



/* These also look like they were junk that got cleaned up
in the move to Zoho.

select *
from dabbledb.Officer do
left join hh_office.Officer ho on ho.id_dabble = do.id
where ho.id_dabble is null;
*/

/* never mind batches */

select *
from dabbledb.Client dc
left join hh_office.Client hc on hc.id_dabble = dc.id
where hc.id_dabble is null;

create index client_id on dabbledb.Client(id);
create index client_id on dabbledb.Visit(client);

insert into Client
(id_dabble, name, insurance, approval, DX, note, Officer_id, DOB, address, phone)
select distinct 0+dc.id, dc.Name, dc.Ins, dc.Approval, dc.DX, dc.note
     , ho.id
     , dc.DOB, dc.address, dc.phone
from dabbledb.Client dc
join dabbledb.Visit dv on dv.client=dc.id -- skip clients with no visits
left join hh_office.Officer ho on ho.id_dabble = dc.officer
left join hh_office.Client hc on hc.id_dabble = dc.id
where hc.id is null;

/* just one stray group
select *
from dabbledb.`Group` dg
left join hh_office.`Group` hg on hg.id_dabble = dg.id
where hg.id_dabble is null;
*/

create index gid on dabbledb.`Group` (id);

/* Looks like all the dabbledb therapists made it to Zoho.

select distinct ds.Therapist
from dabbledb.`Session` ds
join hh_office.Therapist ht on ds.Therapist = ht.name
where ht.id is null;
*/

insert into hh_office.`Session`
 (session_date, time, Group_id, Therapist_id, id_dabble)
select STR_TO_DATE(ds.`date`,'%m/%d/%Y'), ds.time, hg.id, ht.id, ds.id
 from dabbledb.`Session` ds
 join dabbledb.`Group` dg on ds.`group` = dg.id
 join hh_office.`Group` hg on hg.id_dabble = dg.id
 left join hh_office.Therapist ht on ht.name = ds.Therapist
 left join hh_office.`Session` hs on hs.id_dabble = ds.id
where hs.id_dabble is null;


create index visit_id on dabbledb.`Visit` (id);
create index session_id on dabbledb.`Session` (id);

/*
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
*/

/********* **********/

/*
select count(*)
from hh_office.Visit
where id_dabble is not null;
*/

insert into hh_office.Visit (
  charge, id_dabble, Session_id, Client_id, attend_n, client_paid
, note, bill_date, check_date, insurance_paid)
select 0+substr(dg.rate, length('USD $.')) as charge
     , mv.Visit_id_dabble
     , mv.Session_id, mv.Client_id
     , mv.attend_n, mv.client_paid, mv.note
     , mv.bill_date, mv.check_date, mv.insurance_paid
from
(
select dv.id as Visit_id_dabble, hs.id as Session_id, hc.id as Client_id
     , 0+dv.attend as attend_n
     , dv.session as Session_id_dabble
     , 0+substr(dv.`client pd`, length('USD $.')) as client_paid, dv.note
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
join hh_office.Client hc on hc.id_dabble = dv.client
join hh_office.Session hs on hs.id_dabble = dv.session
left join hh_office.Visit hv
  on hv.Session_id = hs.id and hv.Client_id=hc.id
where hv.id is null
) mv
join dabbledb.Session ds on ds.id = mv.Session_id_dabble
join dabbledb.Group dg on ds.group = dg.id
;
