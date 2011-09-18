use hh_office;

create or replace view Attendance_by_Group as
select v.id
     , g.id as group_id, g.name as group_name
     , c.id as client_id, c.name as client_name, o.name as officer_name
     , date_format(s.session_date, '%Y-%m-%d') as session_date
     , attend_n, charge, client_paid
     , insurance_paid, due
     , v.note
from Visit as v
join `Session` as s
  on v.session_id = s.id
join `Group` as g
  on s.group_id = g.id
join Client c
  on v.client_id = c.id
left join Officer o on c.officer_id = o.id;
-- order by g.name, c.name, s.session_date;
select * from hh_office.Attendance_by_Group
order by group_name, client_name, session_date;

select c.name, o.name
from Client c
left join Officer o on c.officer_id = o.id
order by c.name;

select client_id, c.name as client_name,
       session_id, s.session_date, g.name as group_name,
       v.*
from Visit v
join Client c on v.client_id = c.id
join `Session` s on v.session_id = s.id
join `Group` g on s.group_id = g.id;

select g.name as group_name, max(s.session_date) as session_date, c.name as client_name
from Visit v
join `Session` s on v.Session_id = s.id
join `Group` g on s.Group_id = g.id
join Client c on v.Client_id = c.id
group by v.client_id, s.Group_id
order by s.Group_id, max(s.session_date) desc;

