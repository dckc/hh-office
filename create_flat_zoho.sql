drop table if exists attendance_zoho;

create table attendance_zoho as
select c.name, strftime('%m/%d/%Y',s.date) as date, g.name as group_name
     , v.attend, v.client_pd, v.ins_paid as ins_paid, v.note
     , strftime('%m/%d/%Y',v.bill_date) as bill_date
     , strftime('%m/%d/%Y',v.check_date) as check_date
from current_visits v
 join sessions s on v.session = s.id
 join groups g on s.group_id = g.id
 join clients c on v.client = c.id
where 1 = 0;
