<?
/* cribbed from
 http://xataface.com/documentation/tutorial/getting_started/permissions */

// ack:
// http://stackoverflow.com/questions/619610/whats-the-most-efficient-test-of-whether-a-php-string-ends-with-another-string
function ends_with($str, $test) {
  return (strlen($str) >= strlen($test) and
    substr_compare($str, $test, -strlen($test), strlen($test)) === 0);
}

class Audited {

  # ack: User tracking
  # by ADobkin » Tue Oct 23, 2007 11:19 am
  # http://xataface.com/forum/viewtopic.php?t=4215#21205

  # Note also:
  # "It is not possible to have the current
  # timestamp be the default value for one column and
  # the auto-update value for another column"
  # -- http://dev.mysql.com/doc/refman/5.5/en/timestamp.html

  function beforeInsert(&$record){
    $auth =& Dataface_AuthenticationTool::getInstance();
    $user =& $auth->getLoggedInUsername();
    $record->setValue('added_user', $user);
    $record->setValue('modified_user', $user);
  }
  
  function beforeUpdate(&$record){
    $auth =& Dataface_AuthenticationTool::getInstance();
    $user =& $auth->getLoggedInUsername();
    $record->setValue('modified_user', $user);
  }
}


class conf_ApplicationDelegate {
  function getRoles(&$record){
    $auth =& Dataface_AuthenticationTool::getInstance();
    $user =& $auth->getLoggedInUser();
    $username = $auth->getLoggedInUsername();
    if ( $user and (
		    $user->val('role') == 'ADMIN'
		    or $user->val('role') == 'MANAGER' )){
      return $user->val('role');
    } else if (ends_with($username, '@hopeharborkc.com')) {
      return 'READ ONLY';
    } else {
      //session_destroy() produces warnings; seems to be superfluous.
      //session_destroy();
      return Dataface_PermissionsTool::NO_ACCESS();
    }
  }

  function block__custom_stylesheets2 () {
    echo '<link rel="stylesheet" href="./midwest.css" />';
    echo "<link rel='stylesheet' href='av/jqac/jquery.autocomplete.css' />";
  }


  function beforeHandleRequest(){
    $query =& Dataface_Application::getInstance()->getQuery();
    if ( !$_POST and !isset($query['-sort'])) {
      if ( $query['-table'] == 'Session') {
	$query['-sort'] = 'session_date desc';
      }
      if ( $query['-table'] == 'Client') {
	$query['-sort'] = 'name asc';
      }
    }
  }
}
?>
