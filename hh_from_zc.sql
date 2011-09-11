SET sql_mode='ANSI_QUOTES';
use hh_office;

truncate table Therapist;

insert into Therapist (id, name)
select null, name
from zc.Therapist;

insert into "Group" (
  id, name, rate, evaluation,
  id_zoho, id_dabble )
select null, name, rate, evaluation
     , id_zoho, id_dabble
from zc.Group;
