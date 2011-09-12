<?
class tables_Session {
  function getTitle(&$record){
    return $record->strval('session_date');
  }

  function titleColumn(){
    return 'session_date';
  }
}
?>
