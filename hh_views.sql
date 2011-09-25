-- initial caps a la
-- http://xataface.com/documentation/tutorial/getting_started/first_application
-- but I'm going with just id as the primary key, rather than TreatmentID

SET sql_mode='ANSI_QUOTES';
use zc;

create or replace view zc."Group" as
select Name as name, 0+rate as rate, 0 + eval as evaluation
     , primkey as id_zoho, id_dabble
from zc.zcfrm_group;



/* TODO: Test that these match somehow.
 * In oracle, I could signal test failure with 1/0, but mysql just returns null.
 */
select (select count(*) from zc.zcfrm_session) as form_count,
       (select count(*) from zc.zcrel_session_group_name
        where t_765721000000011546_PK is null) as null_group_count,
       (select count(*) from zc.zcfrm_session
        where Therapist is null) as null_therapist_count,
       (select count(*) from zc.zcrel_session_group_name) as rel_count,
       (select count(*) from zc.Session) as c1;



select
   (select count(*) from zc.zcfrm_client) as c_in
 , (select count(*) from zc.Client) as c_out;

/* got all of them?
select * from zc.zcfrm_client
left join Client
on zc.zcfrm_client.pkey = Client.id
where Client.id = null
order by zc.zcfrm_client.Name;
*/

