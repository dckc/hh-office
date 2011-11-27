<?php
class actions_make_claims {
  /** TODO: use POST instead of GET? */
  function handle(&$params){
    $app =& Dataface_Application::getInstance();
    
    $query =& $app->getQuery();
    $records = df_get_selected_records($query);
    
    $claim = 0;
    $service_line = 1;
    $prev_client = 0;

    foreach ($records as $k => $record){
      $client_id = $record->val('client_id');
      if (($client_id != $prev_client)
	  || ($service_line > 6)) {
	$prev_client = $client_id;
	$claim++;
	$service_line = 1;
	echo "<br />claim $claim<br />";

      }

      $client_name = $record->val('name');
      $session_date = $record->getValueAsString('session_date');
      $group_name = $record->val('group_name');
      echo "line $service_line $client_name $session_date $group_name<br />";

      /*
      do_or_die("update Visit v
              join Client c
              on v.Client_id = c.id
              set v.Client_id = $chosen_id
              where c.name = '$chosen_name'");
      echo "Updated visits with clients named $chosen_name
            to client $chosen_id.<br />";
      */

      $service_line++;
    }
    
  }
  }

?>