<?php
class actions_merge_dups {
  /** TODO: use POST instead of GET. */
  function handle(&$params){
    $app =& Dataface_Application::getInstance();
    
    $query =& $app->getQuery();
    $records = df_get_selected_records($query);
    
    foreach ($records as $k => $record){
      $chosen_id = $record->val('id');
      $chosen_name = $record->val('name');
      
      do_or_die("update Visit v
              join Client c
              on v.Client_id = c.id
              set v.Client_id = $chosen_id
              where c.name = '$chosen_name'");
      echo "Updated visits with clients named $chosen_name
            to client $chosen_id.<br />";
      
      do_or_die("delete from Client
              where name = '$chosen_name'
              and id != $chosen_id");
      echo "Deleted clients named $chosen_name other than $chosen_id.<br />";
    }
    
  }
  }

function do_or_die($sql) {
  $result = df_query($sql, null, true);
  if ( !$result ) throw new Exception(mysql_error(df_db()));
}
?>