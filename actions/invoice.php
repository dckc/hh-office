<?php
class actions_invoice {
    function handle(&$params){
      $app =& Dataface_Application::getInstance();
      $record =& $app->getRecord();
      $id = $record->val('id');

      $body = "<br /><br />";

      $summary = query_result($app->db(), "
select name, charges, client_paid, insurance_paid, balance
     , current_timestamp as invoice_date
from hh_office.Client c
where c.id = '$id'");

      $detail = query_result($app->db(), "
select session_date, group_name, charge, client_paid, insurance_paid, due
from hh_office.Attendance
where client_id = '$id'");

      df_display(array('summary'=>$summary[0],
		       'detail'=>$detail),
		 'invoice.html');
    }

  }

function query_result($db, $sql) {
  $result = mysql_query($sql, $db);
  if ( !$result ) throw new Exception(mysql_error(df_db()));
  
  while($row = mysql_fetch_assoc($result))
    {
      $data[] = $row;
    }
  mysql_free_result($result);
  
  return $data;
}

?>
