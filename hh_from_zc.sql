SET sql_mode='ANSI_QUOTES';
use hh_office;

truncate table Therapist;
truncate table "Group";
truncate table "Session";
truncate table "Client";
truncate table "Visit";

insert into Therapist (id, name)
select null, name
from zc.Therapist;

insert into "Group" (
  id, name, rate, evaluation,
  id_zoho, id_dabble )
select null, name, rate, evaluation
     , id_zoho, id_dabble
from zc."Group";

insert into "Session" (
 id, session_date, Therapist_id, time, Group_id,
 id_zoho, id_dabble
)
select null
     , session_date
     , Therapist_id
     , time
     , Group_id_zoho
     , s.id_zoho
     , s.id_dabble
from zc.Session s
join "Group" g on g.id_zoho = s.Group_id_zoho;

insert into Officer (
 name, email, id_zoho, id_dabble
)
select name, email, id_zoho, id_dabble
from zc.Officer;

insert into Client (
       name, insurance, approval, DX, note
     , address, phone, DOB, file, file_site, file_opened, ho.Officer_id
     , id_zoho, id_dabble
)
select
       zc.name, insurance, approval, DX, note
     , address, phone, DOB, file, file_site, file_opened, ho.id as Officer_id
     , zc.id_zoho, zc.id_dabble
from zc.Client zc
left join Officer ho on ho.id_zoho = zc.Officer_id_zoho;


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
     , v.id_zoho as id_zoho, v.id_dabble
from zc.Visit v
join Client c on v.Client_id_zoho = c.id_zoho
join "Session" s on v.Session_id_zoho = s.id_zoho;
