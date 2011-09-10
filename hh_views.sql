-- initial caps a la
-- http://xataface.com/documentation/tutorial/getting_started/first_application
-- but I'm going with just id as the primary key, rather than TreatmentID

create table Treatment (
  id int not null auto_increment primary key,
  name varchar(80) not null,
  rate decimal(6,2) not null,
  evaluation bool not null,
  id_zoho varchar(80),
  id_dabble varchar(80)
) as
select pkey as id, Name as name, rate, eval, primkey, id_dabble
from zc.zcfrm_group;

-- select str_to_date('2011-01-01', '%Y-%m-%d');

-- drop table Therapist;
create table Therapist (
  id int not null auto_increment primary key,
  name varchar(80) not null
) as
select distinct null as id, therapist as name
from zc.zcfrm_session
where therapist is not null;

create index Therapist_name on Therapist (name);

-- drop table session;
create table Session (
  id int not null auto_increment primary key,
  session_date date not null,
  therapist_id int,
  time varchar(20),
  treatment_id int not null,
  id_zoho varchar(80),
  id_dabble varchar(80)
) as
select s.pkey as id
     , str_to_date(s.date_field, '%Y-%m-%d') as session_date
     , t.id as therapist_id
     , s.Time as time
     , g.pkey as treatment_id
     , s.primkey as id_zoho
     , s.id_dabble
from hh_office.zcrel_session_group_name as sRg
join zcfrm_session as s
on s.primkey = sRg.t_765721000000012056_PK
join zcfrm_group as g
on g.primkey = sRg.t_765721000000011546_PK
join Therapist t
on t.name = s.Therapist;

-- ugh. encoding problem: Fiehler, Tanner (ADV - $15/session; must bring â‰¥ $20/week to attend)

drop table if exists Client;
create table Client (
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
  officer_id int,
  id_zoho varchar(80),
  id_dabble varchar(80)
) as
select c.pkey as id, c.Name as name, Ins as insurance, Approval as approval, DX, Note as note
     , address, phone, DOB, File as file, file_site, file_opened, o.pkey as officer_id
     , c.primkey as id_zoho, c.id_dabble
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

-- drop view zvisit;
create table Visit (
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
  check_date date,
  id_zoho varchar(80),
  id_dabble varchar(80)
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
     , v.primkey, v.id_dabble
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

select t.name as `Group`, c.name as `Client`, date_format(s.session_date, '%b %d \'%y') as `Session`
     , attend_n, charge, client_paid, insurance_paid, due
     , due - (charge - client_paid - case when insurance_paid is null then 0 else insurance_paid end) as delta
from Visit as v
join Session as s
  on v.session_id = s.id
join Treatment as t
  on s.treatment_id = t.id
join Client c
  on v.client_id = c.id
order by t.name, c.name, s.session_date;


select t.name as `Group`, c.name as `Client`
     , date_format(min(s.session_date), '%b %d \'%y') as `Start`
     , date_format(max(s.session_date), '%b %d \'%y') as `End`
     , sum(attend_n) as attend_n, sum(charge) as `Charges`, sum(client_paid) as `Client Paid`
     , sum(case when insurance_paid is null then 0 else insurance_paid end) as insurance_paid, sum(due) as due
from Visit as v
join Session as s
  on v.session_id = s.id
join Treatment as t
  on s.treatment_id = t.id
join Client as c
  on v.client_id = c.id
group by t.id, c.id
order by t.name, c.name
;

select distinct t.id as group_id, t.name as `Group`
     , c.id as client_id, c.name as `Client`
     , sum(v.attend_n) as attend_n, sum(v.charge) as `Charges`, sum(v.client_paid) as `Client Paid`
     , sum(case when v.insurance_paid is null then 0 else v.insurance_paid end) as insurance_paid, sum(v.due) as due
from Visit v
  join Session as s on v.session_id = s.id
  join Treatment as t on s.treatment_id = t.id
  join Client as c on v.client_id = c.id
group by t.id, c.id
order by t.name, c.name
;

select distinct g.id as group_id, g.name as `Group`
     , c.id as client_id, c.name as `Client`
from zvisit v
  join zsession s on v.session_id = s.id
  join zgroup g on s.group_id = g.id
  join zclient c on v.client_id = c.id
order by g.name, c.name;


/*************
 * Amount due report
 */
select * from (
select min(s.session_date) as Earliest
     , max(s.session_date) as Latest
     , c.name as Client
     , sum(v.charge) as Charges
     , sum(v.client_paid) as `Client pd`
     , sum(v.insurance_paid) as `Ins. pd`
     , sum(v.due) as Due
from zclient as c
join zvisit as v on v.client_id = c.id
join zsession as s on v.session_id = s.id
group by c.id
) as report order by Due desc;
