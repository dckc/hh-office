<?
/* cribbed from
 http://xataface.com/documentation/tutorial/getting_started/permissions */

// ack:
// http://stackoverflow.com/questions/619610/whats-the-most-efficient-test-of-whether-a-php-string-ends-with-another-string
function ends_with($str, $test) {
  return substr_compare($str, $test, -strlen($test), strlen($test)) === 0;
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
      session_destroy();
      return Dataface_PermissionsTool::NO_ACCESS();
    }
  }

  function block__custom_stylesheets2() {
    echo '<link rel="stylesheet" href="./midwest.css" />';
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
