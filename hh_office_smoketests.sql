
select t.name as `Group`, c.name as `Client`, date_format(s.session_date, '%b %d \'%y') as `Session`
     , attend_n, charge, client_paid, insurance_paid, due
     , due - (charge - client_paid - case when insurance_paid is null then 0 else insurance_paid end) as delta
from Visit as v
join Session as s
  on v.session_id = s.id
join Treatment as t
  on s.treatment_id = t.id
join Client c
  on v.client_id = c.id
order by t.name, c.name, s.session_date;


select t.name as `Group`, c.name as `Client`
     , date_format(min(s.session_date), '%b %d \'%y') as `Start`
     , date_format(max(s.session_date), '%b %d \'%y') as `End`
     , sum(attend_n) as attend_n, sum(charge) as `Charges`, sum(client_paid) as `Client Paid`
     , sum(case when insurance_paid is null then 0 else insurance_paid end) as insurance_paid, sum(due) as due
from Visit as v
join Session as s
  on v.session_id = s.id
join Treatment as t
  on s.treatment_id = t.id
join Client as c
  on v.client_id = c.id
group by t.id, c.id
order by t.name, c.name
;

select distinct t.id as group_id, t.name as `Group`
     , c.id as client_id, c.name as `Client`
     , sum(v.attend_n) as attend_n, sum(v.charge) as `Charges`, sum(v.client_paid) as `Client Paid`
     , sum(case when v.insurance_paid is null then 0 else v.insurance_paid end) as insurance_paid, sum(v.due) as due
from Visit v
  join Session as s on v.session_id = s.id
  join Treatment as t on s.treatment_id = t.id
  join Client as c on v.client_id = c.id
group by t.id, c.id
order by t.name, c.name
;

select distinct g.id as group_id, g.name as `Group`
     , c.id as client_id, c.name as `Client`
from zvisit v
  join zsession s on v.session_id = s.id
  join zgroup g on s.group_id = g.id
  join zclient c on v.client_id = c.id
order by g.name, c.name;


/*************
 * Amount due report
 */
select * from (
select min(s.session_date) as Earliest
     , max(s.session_date) as Latest
     , c.name as Client
     , sum(v.charge) as Charges
     , sum(v.client_paid) as `Client pd`
     , sum(v.insurance_paid) as `Ins. pd`
     , sum(v.due) as Due
from Client as c
join Visit as v on v.client_id = c.id
join Meeting as s on v.session_id = s.id
group by c.id
) as report order by Due desc;