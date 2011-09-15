/*************
 * Amount due report
 */

use hh_office;

select * from hh_office.Client_Balances
order by due desc, client_name;

-- http://www.bluebox.net/news/2009/07/mysql_encoding
-- show variables like 'char%'; 