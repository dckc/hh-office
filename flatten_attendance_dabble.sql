select  c.name, s.date, g.name,
 case when v.attend = 'true' then 1 else 0 end, v.client_pd, v.ins_paid, v.note, v.bill_date, v.check_date
from visits v
 join sessions s on v.session = s.id
 join groups g on s.group_id = g.id
 join clients c on v.client = c.id
order by c.name, s.date desc;
