SET sql_mode='ANSI_QUOTES';
use hh_office;

truncate table Visit;
truncate table `Session`;
truncate table `Group`;
truncate table Therapist;
truncate table Client;
truncate table Officer;
truncate table Office;

insert into `Group` (
  id, name, rate, evaluation,
  id_zoho, id_dabble )
select null, name, rate, Eval
     , primkey, id_dabble
from zc.zcfrm_group
order by name;

-- drop table session;
create or replace view zc.`Session` as
select str_to_date(s.date_field, '%Y-%m-%d') as session_date
     , s.Therapist as Therapist_name
     , s.Time as time
     , g.primkey as Group_id_zoho
     , s.primkey as id_zoho
     , s.id_dabble
from zc.zcrel_session_group_name as sRg
join zc.zcfrm_session as s
on s.primkey = sRg.t_765721000000012056_PK
join zc.zcfrm_group as g
on g.primkey = sRg.t_765721000000011546_PK;


insert into Therapist (id, name)
select distinct null, Therapist_name
from zc.Session
where Therapist_name > ''
order by Therapist_name;

insert into `Session` (
 id, session_date, Therapist_id, time, Group_id,
 id_zoho, id_dabble
)
select null
     , session_date
     , t.id
     , time
     , g.id
     , s.id_zoho
     , s.id_dabble
from zc.`Session` s
join `Group` g on g.id_zoho = s.Group_id_zoho
left join Therapist t on t.name = s.Therapist_name
order by session_date, g.name;


insert into Office (
  id, name, address, fax, notes
, id_zoho, id_dabble)
select null
     , name, address, fax, notes
     , primkey as id_zoho, id_dabble
from zc.zcfrm_office
order by name;

create or replace view zc.Officer as
select zo.Name as name, email, zof.primkey as Office_id_zoho, zo.primkey as id_zoho, zo.id_dabble
from zc.zcfrm_officer zo
left join zc.zcrel_officer_office_name oro
  on oro.t_765721000000011780_PK = zo.primkey
left join zc.zcfrm_office zof on oro.t_765721000000011877_PK = zof.primkey;

insert into Officer (
 name, email, Office_id, id_zoho, id_dabble
)
select zo.name, zo.email, hof.id as office_id, zo.id_zoho, zo.id_dabble
from zc.Officer zo
left join Office hof on zo.Office_id_zoho = hof.id_zoho
order by name;

-- ugh. encoding problem: Fiehler, Tanner (ADV - $15/session; must bring â‰¥ $20/week to attend)

create or replace view zc.Client as
select c.Name as name, Ins as insurance, Approval as approval, DX, Note as note
     , address, phone, DOB, File as file, file_site, file_opened, o.primkey as Officer_id_zoho
     , c.primkey as id_zoho, c.id_dabble
from zc.zcfrm_client as c
left join zc.zcrel_client_officer_name as cRo
  on cRo.t_765721000000011616_PK = c.primkey
left join zc.zcfrm_officer as o
  on cRo.t_765721000000011780_PK = o.primkey;


insert into Client (
       name, insurance, approval, DX, note
     , address, phone, DOB, file, file_site, file_opened, Officer_id
     , id_zoho, id_dabble
)
select
       zc.name, insurance, approval, DX, note
     , address, phone, DOB, file, file_site, file_opened, ho.id as Officer_id
     , zc.id_zoho, zc.id_dabble
from zc.Client zc
left join Officer ho on ho.id_zoho = zc.Officer_id_zoho
order by name;


create unique index session_primkey on zc.zcfrm_session (primkey);
create unique index client_primkey on zc.zcfrm_client (primkey);
create unique index visit_primkey on zc.zcfrm_visit (primkey);
create index zrvs on zc.zcrel_visit_session (t_765721000000011230_PK);

create or replace view zc.Visit as
select s.primkey as Session_id_zoho
     , c.primkey as Client_id_zoho
     , cast(attend_n as unsigned integer) as attend_n
     , convert(charge, decimal(6, 2)) as charge
     , convert(client_pd, decimal(6, 2)) as client_paid
     , convert(ins_paid, decimal(6, 2)) as insurance_paid
     , convert(Due, decimal(6, 2)) as due
     , v.note
     , str_to_date(v.bill_date, '%Y-%m-%d') as bill_date
     , str_to_date(v.check_date, '%Y-%m-%d') as check_date
     , v.primkey as id_zoho, v.id_dabble
from zc.zcrel_visit_client as vRc
join zc.zcfrm_visit as v
  on v.primkey = vRc.t_765721000000011230_PK
join zc.zcfrm_client as c
  on c.primkey = vRc.t_765721000000011616_PK
join zc.zcrel_visit_session as vRs
  on v.primkey = vRs.t_765721000000011230_PK
join zc.zcfrm_session as s
  on s.primkey = t_765721000000012056_PK;


insert into Visit (
       Session_id
     , Client_id
     , attend_n
     , charge
     , client_paid
     , insurance_paid
     , due
     , note
     , bill_date
     , check_date
     , id_zoho, id_dabble )
select s.id as Session_id
     , c.id as Client_id
     , v.attend_n
     , v.charge
     , v.client_paid
     , v.insurance_paid
     , v.due
     , v.note
     , v.bill_date
     , v.check_date
     , v.id_zoho, v.id_dabble
from zc.Visit v
join Client c on v.Client_id_zoho = c.id_zoho
join `Session` s on v.Session_id_zoho = s.id_zoho
order by s.session_date, c.name;

/* I'm not seeing a client name for some visits. What's up?
select
(select count(*) from zc.Visit) as zc_visits,
(select count(*) from hh_office.Visit) as hh_visits;


select *
from Visit v
left join Client c on v.Client_id = c.id
where c.id is null
-- and v.id_dabble is not null
;

select *
from zc.Visit v
left join zc.Client c on v.Client_id_zoho = c.id_zoho
where c.id_zoho is null
-- and v.id_dabble is not null
;
 */
