use hh_office;

drop view Attendance_by_Group;

create or replace view Attendance as
select v.id
     , g.id as group_id, g.name as group_name, g.rate as group_rate
     , c.id as client_id, c.name as client_name, o.name as officer_name
     , s.id as session_id, date_format(s.session_date, '%Y-%m-%d') as session_date
     , attend_n, charge, client_paid
     , insurance_paid, due
     , v.note
     , charge - client_paid -
      case when insurance_paid is null then 0 else insurance_paid end as calc_due
from Visit as v
join `Session` as s on v.Session_id = s.id
join `Group` as g on s.Group_id = g.id
join Client c on v.Client_id = c.id
left join Officer o on c.Officer_id = o.id;
-- order by g.name, c.name, s.session_date;
select * from hh_office.Attendance
order by group_name, client_name, session_date;

select *
from Attendance
where attend_n != 0
and charge != group_rate
order by session_date;

select group_name as group_name, max(session_date) as session_date, sum(calc_due) as due, client_name
from Attendance a
group by client_id, group_id
order by group_name, max(session_date) desc;

select max(session_date) recent
     , c.id as client_id, c.name as client_name
     , g.id as group_id, g.name as group_name
from Client c
join Visit v on v.Client_id = c.id
join `Session` s on v.Session_id = s.id
join `Group` g on s.Group_id = g.id
where datediff(now(), session_date)< 90
group by c.id, g.id
order by recent desc
;

select *
from `Session`
where session_date < makedate(2006,1);

drop table each_month;

create table period as
(select year, month, quarter, half, STR_TO_DATE(CONCAT_WS('-',y.year,m.month,1),'%Y-%m-%d') as first
from
(select 2006 as year
union all select 2007
union all select 2008
union all select 2009
union all select 2010
union all select 2011
union all select 2012) as y,
(         select 1 as month, 1 as quarter, 1 as half
union all select 2 as month, 1 as quarter, 1 as half
union all select 3 as month, 1 as quarter, 1 as half
union all select 4 as month, 2 as quarter, 1 as half
union all select 5 as month, 2 as quarter, 1 as half
union all select 6 as month, 2 as quarter, 1 as half
union all select 7 as month, 3 as quarter, 2 as half
union all select 8 as month, 3 as quarter, 2 as half
union all select 9 as month, 3 as quarter, 2 as half
union all select 10 as month, 4 as quarter, 2 as half
union all select 11 as month, 4 as quarter, 2 as half
union all select 12 as month, 4 as quarter, 2 as half
) as m);

/* How many sessions each quarter? */
select period.first, count(distinct s.id)
from `Session` s
join period on year(s.session_date) = period.year
           and quarter(s.session_date) = period.quarter
group by period.year, period.quarter;

select * from Attendance;

select period.first, count(distinct id)
from Attendance a
join period on year(a.session_date) = period.year
           and quarter(a.session_date) = period.quarter
group by period.year, period.quarter;

/* how many visits per session on average? 6.348 */
select (select count(*) from Visit)
/ (select count(*) from `Session`);

select each_month.first, c.id as client_id, c.name as client_name,
  count(v.id) visits,
  sum(charge - client_paid -
      case when insurance_paid is null then 0 else insurance_paid end) as balance
from Client c
join Visit v on v.Client_id = c.id
join `Session` s on v.Session_id = s.id,
each_month
where session_date < each_month.first
group by each_month.first, c.id
having visits > 0
order by each_month.first, c.name;



select session_date, datediff(now(), session_date)
from `Session`;