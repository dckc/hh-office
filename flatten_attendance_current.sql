select 'Name', 'date', 'Group Name', 'Attend', 'client pd', 'ins paid $'
     , 'note', 'bill date', 'check date';

select c.name, strftime('%m/%d/%Y',s.date), g.name
     , v.attend, v.client_pd, v.ins_paid, v.note
     , strftime('%m/%d/%Y',v.bill_date)
     , strftime('%m/%d/%Y',v.check_date)
from current_visits v
 join sessions s on v.session = s.id
 join groups g on s.group_id = g.id
 join clients c on v.client = c.id
order by c.name, s.date desc;
