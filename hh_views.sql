

create or replace view zgroup
as
select pkey as id, Name as name, rate, eval
from zcfrm_group;

-- select str_to_date('2011-01-01', '%Y-%m-%d');

drop table zsession;
create table zsession (
  id int not null auto_increment primary key,
  session_date date not null,
  therapist varchar(80),
  time varchar(20),
  group_id int not null 
) as
select s.pkey as id
     , str_to_date(s.date_field, '%Y-%m-%d') as session_date
     , s.Therapist as therapist
     , s.Time as time
     , g.pkey as group_id
from hh_office.zcrel_session_group_name as sRg
join zcfrm_session as s
on s.primkey = sRg.t_765721000000012056_PK
join zcfrm_group as g
on g.primkey = sRg.t_765721000000011546_PK;

select * from zcfrm_session
left join zsession
on zcfrm_session.pkey = zsession.id
where zsession.id = null
order by zcfrm_session.date_field;


-- ugh. encoding problem: Fiehler, Tanner (ADV - $15/session; must bring â‰¥ $20/week to attend)

drop table zclient;
create table zclient (
  id int not null auto_increment primary key,
  name varchar(80) not null,
  insurance varchar(80),
  approval text,
  DX varchar(80),
  note text,
  address varchar(80),
  phone varchar(80),
  DOB date,
  file varchar(80),
  file_site varchar(80), -- enum?
  file_opened date,
  officer_id int
) as
select c.pkey as id, c.Name as name, Ins as insurance, Approval as approval, DX, Note as note
     , address, phone, DOB, File as file, file_site, file_opened, o.pkey as officer_id
from hh_office.zcfrm_client as c
left join hh_office.zcrel_client_officer_name as cRo
  on cRo.t_765721000000011616_PK = c.primkey
left join hh_office.zcfrm_officer as o
  on cRo.t_765721000000011780_PK = o.primkey;

-- got all of them?
select * from zcfrm_client
left join zclient
on zcfrm_client.pkey = zclient.id
where zclient.id = null
order by zcfrm_client.Name;

create unique index session_primkey on zcfrm_session (primkey);
create unique index client_primkey on zcfrm_client (primkey);
create unique index visit_primkey on zcfrm_visit (primkey);

drop view zvisit;
create table zvisit (
  id int not null auto_increment primary key,
  session_id int not null,
  client_id int not null,
  attend_n int not null,
  charge decimal(6,2) not null,
  client_pd decimal(6, 2) not null,
  insurance_paid decimal(6, 2),
  due decimal(6, 2) not null,
  note text,
  bill_date date,
  check_date date
) as
select v.pkey as id
     , s.pkey as session_id
     , c.pkey as client_id
     , cast(attend_n as unsigned integer) as attend_n
     , convert(charge, decimal(6, 2)) as charge
     , convert(client_pd, decimal(6, 2)) as client_paid
     , convert(ins_paid, decimal(6, 2)) as insurance_paid
     , convert(Due, decimal(6, 2)) as due
     , v.note
     , str_to_date(v.bill_date, '%Y-%m-%d') as bill_date
     , str_to_date(v.check_date, '%Y-%m-%d') as check_date
from hh_office.zcrel_visit_client as vRc
join hh_office.zcfrm_visit as v
  on v.primkey = vRc.t_765721000000011230_PK
join hh_office.zcfrm_client as c
  on c.primkey = vRc.t_765721000000011616_PK
join hh_office.zcrel_visit_session as vRs
  on v.primkey = vRs.t_765721000000011230_PK
join hh_office.zcfrm_session as s
  on s.primkey = t_765721000000012056_PK;


select * from zcfrm_visit
left join zvisit
on zcfrm_visit.pkey = zvisit.id
where zvisit.id = null;
