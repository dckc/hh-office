<?php
class actions_make_claims {
  /** TODO: use POST instead of GET? */
  function handle(&$params){
    $app =& Dataface_Application::getInstance();
    $key = $app->_conf['_database']['report_key'];
    
    $query =& $app->getQuery();
    $records = df_get_selected_records($query);
    $selected_visits = array_values($records);
    $visits = '';

    foreach ($selected_visits as $record){
      if ($visits) { $visits .= ','; }
      $visits .= $record->val('id');
    }

    header('Location: dispatch.cgi/claim_sync/make_claims?'
	   . 'key=' . $key . '&visits=' . $visits);
    exit;
  }
}

?>
