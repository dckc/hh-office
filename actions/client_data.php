<?php
/**
 * cribbed from RecordBrowser_data.php
 */
class actions_client_data {
  function handle(&$params){
    $app =& Dataface_Application::getInstance();
    //$out = array();
    $query =& $app->getQuery();
    $records = df_get_records_array($query['-table'], $query);
    header("Content-type: text/plain; charset=".$app->_conf['oe']);
    foreach ($records as $record){
      // This record has a single key column so we return its value
      $value = $record->val(reset(array_keys($record->_table->keys())));
			
      // Now let's get the text that we are using for this option
      $text = $record->display($query['-text']);

      echo "$text|$value\n";
    }
  }
}