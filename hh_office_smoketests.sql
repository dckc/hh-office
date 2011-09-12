
select g.name as `Group`, c.name as `Client`, date_format(s.session_date, '%b %d \'%y') as `Session`
     , attend_n, charge, client_paid, insurance_paid, due
     , due - (charge - client_paid - case when insurance_paid is null then 0 else insurance_paid end) as delta
from Visit as v
join `Session` as s
  on v.Session_id = s.id
join `Group` as g
  on s.Group_id = g.id
join Client c
  on v.Client_id = c.id
order by g.name, c.name, s.session_date;


select g.name as `Group`, c.name as `Client`
     , date_format(min(s.session_date), '%b %d \'%y') as `Start`
     , date_format(max(s.session_date), '%b %d \'%y') as `End`
     , sum(attend_n) as attend_n, sum(charge) as `Charges`, sum(client_paid) as `Client Paid`
     , sum(case when insurance_paid is null then 0 else insurance_paid end) as insurance_paid, sum(due) as due
from Visit as v
join `Session` as s
  on v.session_id = s.id
join `Group` as g
  on s.Group_id = g.id
join Client as c
  on v.client_id = c.id
group by g.id, c.id
order by g.name, c.name
;

select distinct g.id as group_id, g.name as `Group`
     , c.id as client_id, c.name as `Client`
     , sum(v.attend_n) as attend_n, sum(v.charge) as `Charges`, sum(v.client_paid) as `Client Paid`
     , sum(case when v.insurance_paid is null then 0 else v.insurance_paid end) as insurance_paid, sum(v.due) as due
from Visit v
  join Session as s on v.Session_id = s.id
  join `Group` as g on s.Group_id = g.id
  join Client as c on v.Client_id = c.id
group by g.id, c.id
order by g.name, c.name
;

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
join Visit as v on v.Client_id = c.id
join `Session` as s on v.Session_id = s.id
group by c.id
) as report order by Due desc;