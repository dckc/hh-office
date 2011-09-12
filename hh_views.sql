-- initial caps a la
-- http://xataface.com/documentation/tutorial/getting_started/first_application
-- but I'm going with just id as the primary key, rather than TreatmentID

SET sql_mode='ANSI_QUOTES';
use zc;

create or replace view zc."Group" as
select Name as name, 0+rate as rate, 0 + eval as evaluation
     , primkey as id_zoho, id_dabble
from zc.zcfrm_group;

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

/* TODO: Test that these match somehow.
 * In oracle, I could signal test failure with 1/0, but mysql just returns null.
 */
select (select count(*) from zc.zcfrm_session) as form_count,
       (select count(*) from zc.zcrel_session_group_name
        where t_765721000000011546_PK is null) as null_group_count,
       (select count(*) from zc.zcfrm_session
        where Therapist is null) as null_therapist_count,
       (select count(*) from zc.zcrel_session_group_name) as rel_count,
       (select count(*) from zc.Session) as c1;

create or replace view Officer as
select Name as name, email, primkey as id_zoho, id_dabble
from zc.zcfrm_officer;

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

select
   (select count(*) from zc.zcfrm_client) as c_in
 , (select count(*) from zc.Client) as c_out;

/* got all of them?
select * from zc.zcfrm_client
left join Client
on zc.zcfrm_client.pkey = Client.id
where Client.id = null
order by zc.zcfrm_client.Name;
*/

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


