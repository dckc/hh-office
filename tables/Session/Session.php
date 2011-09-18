<?
class tables_Session {
  function getTitle(&$record){
    return $record->strval('session_date');
  }

  function titleColumn(){
    return 'session_date';
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
