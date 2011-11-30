<?php
class actions_make_claims {
  /** TODO: use POST instead of GET? */
  function handle(&$params){
    $app =& Dataface_Application::getInstance();
    
    $query =& $app->getQuery();
    $records = df_get_selected_records($query);

    do_or_die("update Attendance_all set claim_uid=null
               where ins_status='billable'");
    $claim = array();
    $service_line = 1;
    $prev_client = 0;

    $selected_visits = array_values($records);
    usort($selected_visits, 'by_client');

    foreach ($selected_visits as $record){
      $client_id = $record->val('Client_id');
      if (($client_id != $prev_client)
	  || ($service_line > 6)) {
	set_claim($prev_client, $claim);
	$prev_client = $client_id;
	$claim = array();
	$service_line = 1;
	echo "<br />";

      }

      $session_date = $record->getValueAsString('session_date');
      $group_name = $record->val('group_name');
      echo "line $service_line $client_id $session_date $group_name<br />";

      $claim[] = $record->val('id');
      $service_line++;
    }

    set_claim($prev_client, $claim);
  }
  }

function by_client($a, $b) {
  $client_a = $a->val('Client_id');
  $client_b = $b->val('Client_id');

  if ($client_a == $client_b) {
    return 0;
  }
  return ($client_a < $client_b) ? -1 : 1;
}

function set_claim($client_id, $visits) {
  if (! count($visits) > 0) {
    return;
  }

  $visit_list = implode(',', $visits);
  $claim_uid = uniqid($client_id . ':');
  $dml = "update Visit
          set claim_uid = '$claim_uid'
          where id in ($visit_list)";

  echo "$dml; ...";
  do_or_die($dml);
  echo " done.<br />";
}

function do_or_die($sql) {
  $result = df_query($sql, null, true);
  if ( !$result ) throw new Exception(mysql_error(df_db()));
}
?>