<?php
class actions_invoice {
    function handle(&$params){
      $app =& Dataface_Application::getInstance();
      $record =& $app->getRecord();

      /* Update the balance here, just in case things get wonky. */
      $id = $record->val('id');
      $record->table()->getDelegate()->update_balance($id);

      $body = "<br /><br />";

      $summary = query_result($app->db(), "
select name, charges, client_paid, insurance_paid, balance
     , current_timestamp as invoice_date
from hh_office.Client c
where c.id = '$id'");

      $summary = $summary[0];
      setlocale(LC_ALL, 'en_US');
      $summary['charges'] = number_format($summary['charges'], 2);
      $summary['client_paid'] = number_format($summary['client_paid'], 2);
      $summary['insurance_paid'] = number_format($summary['insurance_paid'], 2);
      $summary['balance'] = number_format($summary['balance'], 2);

      $detail = query_result($app->db(), "
select session_date, group_name
     , attend_n, charge, client_paid, insurance_paid, due
from hh_office.Attendance
where client_id = '$id'
order by session_date");

      df_display(array('summary'=>$summary,
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
