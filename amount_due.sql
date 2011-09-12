/*************
 * Amount due report
 */

use hh_office;

create or replace view Client_Balances as
select c.id
     , min(s.session_date) as earliest
     , max(s.session_date) as latest
     , c.name as client_name
     , sum(v.charge) as charges
     , sum(v.client_paid) as client_paid
     , sum(v.insurance_paid) as insurance_paid
     , sum(v.due) as due
from Client as c
join Visit as v on v.Client_id = c.id
join `Session` as s on v.Session_id = s.id
group by c.id;

select * from Client_Balances
order by due desc, client_name;

-- http://www.bluebox.net/news/2009/07/mysql_encoding
-- show variables like 'char%'; 