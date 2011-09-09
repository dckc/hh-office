/*************
 * Amount due report
 */
select * from (
select min(s.session_date) as earliest
     , max(s.session_date) as latest
     , c.name as client_name
     , sum(v.charge) as charges
     , sum(v.client_paid) as client_paid
     , sum(v.insurance_paid) as insurance_paid
     , sum(v.due) as due
from Client as c
join Visit as v on v.client_id = c.id
join Session as s on v.session_id = s.id
-- where c.name = 'Adams, Luke' -- not like 'Fiehler%' -- KLUDGE: work around encoding error
group by c.id
) as report order by due desc

-- http://www.bluebox.net/news/2009/07/mysql_encoding
-- show variables like 'char%'; 