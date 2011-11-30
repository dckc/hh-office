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

  function block__tables_menu_head () {
    $app =& Dataface_Application::getInstance();
    $key = $app->_conf['_database']['report_key'];
    echo "<ul class='report_menu'>
            <li><a href='print_report/recent_sessions?key=$key'
                   target='_new'><em>Recent Sign-in Sheets</em></a></li>
         </ul>";
  }

  function block__after_main_section() {
    echo '<script type="text/javascript">
(function () {
    $("form[method=\"post\"] input[type=\"submit\"]").each(function() {
            var save = $(this);
            save.attr("tabindex", 9); //HARDCODED
            save.attr("accesskey", "S");
    });

    // no tabbing through links nor the search form
    $("a, .search_form input").each(function() {
            var a = $(this);
            a.attr("tabindex", -1);
    });

//alert("set tab index on " + tabindex + " fields");
})();
</script>
';
  }

  function session_date__display(&$record){
    return date('m/d/Y', strtotime($record->strval('session_date')));
  }

  // When a session is added, go right to add related visit.
  function after_action_new (&$info) {
    $id = $info['record']->val('id');
    $this->visit_redirect(false, "&id=%3D$id");
  }

  function afterAddRelatedRecord(&$record) {
    $this->visit_redirect(true);
  }

  function visit_redirect($useContext, $extra) {
    $app =& Dataface_Application::getInstance();
    $there = $app->url("-action=new_related_record&-table=Session&-relationship=Visits" . $extra, $useContext);
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
