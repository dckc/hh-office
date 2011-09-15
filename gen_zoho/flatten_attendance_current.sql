select 'Name', 'date', 'Group Name', 'Attend', 'client pd', 'ins paid $'
     , 'note', 'bill date', 'check date';

select c.name, strftime('%m/%d/%Y',s.date), g.name
     , v.attend, v.client_pd
     , case when v.ins_paid is null then 0 else v.ins_paid end
     , v.note
     , case when v.bill_date is null then ''
       else strftime('%m/%d/%Y',v.bill_date) end
     , case when v.check_date is null then ''
       else strftime('%m/%d/%Y',v.check_date) end
from current_visits v
 join sessions s on v.session = s.id
 join groups g on s.group_id = g.id
 join clients c on v.client = c.id
order by c.name, s.date desc;
