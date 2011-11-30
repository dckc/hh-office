

create or replace view Attendance_all as
select v.id
     , g.id as group_id, g.name as group_name, g.rate as group_rate
     , c.id as client_id, c.name as client_name, c.billing_cutoff, c.recent
     , ins.id as policy_id, ins.dx1, ins.dx2
     , co.id as carrier_id, co.name as carrier_name
     , o.name as officer_name
     , s.id as session_id, s.Therapist_id, s.session_date
     , attend_n, v.charge, v.client_paid
     , v.claim_uid
     , v.insurance_paid
     , v.bill_date
     , v.check_date
     , v.note
     , v.charge - v.client_paid -
      case when v.insurance_paid is null then 0 else v.insurance_paid end as due
     , v.cpt
     , case
       when v.check_date is not null then 'paid'
       when v.bill_date is not null then 'billed'
       when ins.id is null then 'no ins'
       when v.cpt is null then 'no CPT'
       when v.attend_n = 0 then 'did not attend'
       else 'billable'
       end as ins_status
from Visit as v
join `Session` as s on v.Session_id = s.id
join `Group` as g on s.Group_id = g.id
join Client c on v.Client_id = c.id
left join Officer o on c.Officer_id = o.id
left join Insurance ins on ins.Client_id = c.id
left join Carrier co on ins.Carrier_id = co.id
;


create or replace view Client_Balances as
select client_id
     , min(session_date) as oldest_session_date
     , max(session_date) as recent
     , sum(charge) as charges
     , sum(client_paid) as client_paid
     , sum(case when insurance_paid is null then 0
           else insurance_paid end) as insurance_paid
     , sum(charge - client_paid -
           case when insurance_paid is null then 0
           else insurance_paid end) as balance
from Attendance_all
where session_date >= billing_cutoff
group by client_id;


/* Around a dozen of these disconnected clients,
perhaps entered and abandoned in dabble?

select distinct c.id, c.name
from Client c
left join Visit v on v.Client_id = c.id
where v.id is null;
*/

SET SQL_SAFE_UPDATES=0;

update `Visit` v
join `Session` s on v.Session_id = s.id
join `Group` g on s.Group_id = g.id
set v.cpt=g.cpt
where v.id > 0
and g.cpt > '';

update Client c
set balance_cached = null
  , c.billing_cutoff = (select min(session_date) from `Session`)
  , c.charges = null
  , c.client_paid = null
  , c.insurance_paid = null
  , c.balance = null;

/* Don't bother billing people with
   no visits newer than 2 years old. */
update Client c
join Client_Balances cb on cb.client_id = c.id
set c.recent = cb.recent,
  c.billing_cutoff = 
  case
    when cb.recent < str_to_date('2009-07-01', '%Y-%m-%d') then null
    else cb.oldest_session_date
  end;

update Client c
join Client_Balances cb on cb.client_id = c.id
set balance_cached = current_timestamp
  , c.charges = cb.charges
  , c.client_paid = cb.client_paid
  , c.insurance_paid = cb.insurance_paid
  , c.balance = cb.balance;

-- select * from Client where billing_cutoff is null;

insert into Batch (name, cutoff)
values ('current', '2011-06-01');

create or replace view Batch_Clients as
select b.name as batch_name, c.id as client_id
from Batch b
join Client c on c.recent >= b.cutoff;

create or replace view Attendance as
select att.*
from Attendance_all att
where att.session_date >= att.billing_cutoff
and att.recent >= (select cutoff from Batch where name = 'current')
;

update Therapist t
join (select t.id, t.name, count(s.id) as weight
from Therapist t
join Session s on s.Therapist_id = t.id
group by t.id
) tw on tw.id = t.id
set t.weight = tw.weight;


-- select * from insurance_visits;

/*
select * from hh_office.Attendance
order by group_name, client_name, session_date;
*/

/* 108 cases where the visit charge does not match the group rate; worth review?

select *
from Attendance
where attend_n != 0
and charge != group_rate
order by session_date;

*/


/*
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
*/


/* how many visits per session on average? 6.348
select (select count(*) from Visit)
/ (select count(*) from `Session`);
*/