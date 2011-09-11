SET sql_mode='ANSI_QUOTES';
use hh_office;

truncate table Therapist;
truncate table "Group";
truncate table "Session";
truncate table "Client";

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
     , Group_id
     , id_zoho
     , id_dabble
from zc.Session;

insert into Officer (
 name, email, id_zoho, id_dabble
)
select name, email, id_zoho, id_dabble
from zc.Officer;

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
left join Officer ho on ho.id_zoho = zc.Officer_id_zoho;

