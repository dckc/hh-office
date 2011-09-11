-- initial caps a la
-- http://xataface.com/documentation/tutorial/getting_started/first_application
-- but I'm going with just id as the primary key, rather than TreatmentID

SET sql_mode='ANSI_QUOTES';
use zc;

create table Therapist (
  id int not null auto_increment primary key,
  name varchar(80) not null
) as
select distinct null as id, therapist as name
from zcfrm_session
where therapist is not null;

create index Therapist_name on Therapist (name);

create or replace view "Group" as
select Name as name, 0+rate as rate, 0 + eval as evaluation
     , primkey as id_zoho, id_dabble
from zcfrm_group;

-- drop table session;
create or replace view `Session` as
select str_to_date(s.date_field, '%Y-%m-%d') as session_date
     , t.id as Therapist_id
     , s.Time as time
     , g.pkey as Group_id
     , s.primkey as id_zoho
     , s.id_dabble
from zcrel_session_group_name as sRg
join zcfrm_session as s
on s.primkey = sRg.t_765721000000012056_PK
join zcfrm_group as g
on g.primkey = sRg.t_765721000000011546_PK
join Therapist t
on t.name = s.Therapist;

create or replace view Officer as
select Name as name, email, primkey as id_zoho, id_dabble
from zcfrm_officer;

-- ugh. encoding problem: Fiehler, Tanner (ADV - $15/session; must bring â‰¥ $20/week to attend)

create or replace view Client as
select c.Name as name, Ins as insurance, Approval as approval, DX, Note as note
     , address, phone, DOB, File as file, file_site, file_opened, o.pkey as Officer_id
     , c.primkey as id_zoho, c.id_dabble
from zcfrm_client as c
left join zcrel_client_officer_name as cRo
  on cRo.t_765721000000011616_PK = c.primkey
left join zcfrm_officer as o
  on cRo.t_765721000000011780_PK = o.primkey;

/* got all of them?
select * from zcfrm_client
left join Client
on zcfrm_client.pkey = Client.id
where Client.id = null
order by zcfrm_client.Name;
*/

create unique index session_primkey on zcfrm_session (primkey);
create unique index client_primkey on zcfrm_client (primkey);
create unique index visit_primkey on zcfrm_visit (primkey);

create or replace view Visit as
select s.pkey as Session_id
     , c.pkey as Client_id
     , cast(attend_n as unsigned integer) as attend_n
     , convert(charge, decimal(6, 2)) as charge
     , convert(client_pd, decimal(6, 2)) as client_paid
     , convert(ins_paid, decimal(6, 2)) as insurance_paid
     , convert(Due, decimal(6, 2)) as due
     , v.note
     , str_to_date(v.bill_date, '%Y-%m-%d') as bill_date
     , str_to_date(v.check_date, '%Y-%m-%d') as check_date
     , v.primkey as id_zoho, v.id_dabble
from zcrel_visit_client as vRc
join zcfrm_visit as v
  on v.primkey = vRc.t_765721000000011230_PK
join zcfrm_client as c
  on c.primkey = vRc.t_765721000000011616_PK
join zcrel_visit_session as vRs
  on v.primkey = vRs.t_765721000000011230_PK
join zcfrm_session as s
  on s.primkey = t_765721000000012056_PK;


