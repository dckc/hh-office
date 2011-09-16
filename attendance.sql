create or replace view Attendance_by_Group as
select g.id as group_id, g.name as group_name
     , c.id as client_id, c.name as client_name
     , date_format(s.session_date, '%Y-%m-%d') as session_date
     , attend_n, charge, client_paid
     , insurance_paid, due
     , v.note
from zvisit as v
join zsession as s
  on v.session_id = s.id
join zgroup as g
  on s.group_id = g.id
join zclient c
  on v.client_id = c.id
order by g.name, c.name, s.session_date
