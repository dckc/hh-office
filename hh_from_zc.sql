SET sql_mode='ANSI_QUOTES';
use hh_office;

truncate table Therapist;
truncate table `Group`;
truncate table `Session`;
truncate table Office;
truncate table Officer;
truncate table Client;
truncate table Visit;

insert into Therapist (id, name)
select distinct null, Therapist_name
from zc.Session
where Therapist_name > ''
order by Therapist_name;

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

create index client_id_zoho on Client(id_zoho);
create index session_id_zoho on Session(id_zoho);

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
