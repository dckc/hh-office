<?
class tables_Session extends Audited {
  function getTitle(&$session){
    $group = $session->getRelatedRecord('Group');
    return ($group->strval('name') . ' ' .
	    date('m/d/Y', strtotime($session->strval('session_date'))) . ' ' .
	    $session->strval('time'));

#$session->strval('session_date');
  }

  function titleColumn(){
    return 'session_date';
  }

  function session_date__display(&$record){
    return date('m/d/Y', strtotime($record->strval('session_date')));
  }

  // When a session is added, go right to add related visit.
  function after_action_new (&$record) {
    $this->visit_redirect();
  }

  function afterAddRelatedRecord(&$record) {
    $this->visit_redirect();
  }

  function visit_redirect() {
    $app =& Dataface_Application::getInstance();
    $there = $app->url('-action=new_related_record&-relationship=Visits');
    #error_log('save and add: ' . $there);
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
