<?
class tables_Session extends Audited {
  function getTitle(&$record){
    return $record->strval('session_date');
  }

  function titleColumn(){
    return 'session_date';
  }

  // When a session is added, go right to add related visit.
  function after_action_new ($record) {
    $app =& Dataface_Application::getInstance();
    $there = $app->url('-action=new_related_record&-relationship=Visits');
    error_log('save and add: ' . $there);
    header('Location: '. $there);
    exit;
  }

#  function time__display(&$record){ 
#    $v = $record->strval('time');
#    $t = strtotime($v);
#    if ($t) {
#      return date(' g:i', $t);
#    } else {
#      return $v;
#    }
#  }
}
?>
