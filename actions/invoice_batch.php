<?php
class actions_invoice_batch {
  /* Ugh... lots of copy-and-paste from invoice.php */

  function handle(&$params) {
    $app =& Dataface_Application::getInstance();

    /* Update balances here, just in case things get wonky. */
    $client = Dataface_Table::loadTable('Client');
    $client->getDelegate()->update_balances();

    $invoices = query_result2($app->db(), "
select c.id, c.name, c.charges, c.client_paid, c.insurance_paid, c.balance
     , current_timestamp as invoice_date, c.invoice_note
from Client c
join Bulk_Invoices bi on c.id = bi.client_id
    ");

    foreach ($invoices as $summary) {
      $id = $summary['id'];
      $detail = query_result2($app->db(), "
select session_date, group_name
     , attend_n, charge, client_paid, insurance_paid, due
from Attendance
where client_id = '$id'
order by session_date");

      df_display(array('summary'=>$summary,
		       'detail'=>$detail),
		 'invoice.html');
    }
  }
}

function query_result2($db, $sql) {
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
	
