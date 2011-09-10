<?
/* cribbed from
 http://xataface.com/documentation/tutorial/getting_started/permissions */

// ack:
// http://stackoverflow.com/questions/619610/whats-the-most-efficient-test-of-whether-a-php-string-ends-with-another-string
function ends_with($str, $test) {
  return substr_compare($str, $test, -strlen($test), strlen($test)) === 0;
}

class conf_ApplicationDelegate {
  /**
   * Returns permissions array.  This method is called every time an action is 
   * performed to make sure that the user has permission to perform the action.
   * @param record A Dataface_Record object (may be null) against which we check
   *               permissions.
   * @see Dataface_PermissionsTool
   * @see Dataface_AuthenticationTool
   */
  function getPermissions(&$record){
    $auth =& Dataface_AuthenticationTool::getInstance();
    $user =& $auth->getLoggedInUser();
    if ( $user and ends_with($auth->getLoggedInUsername(),
			     '@hopeharborkc.com')) {
      return Dataface_PermissionsTool::ALL();
    } else {
      /*
       trigger_error ( 'unknown domain: ' . $auth->getLoggedInUsername(),
		      E_USER_NOTICE );
      */
      return Dataface_PermissionsTool::NO_ACCESS();
    }
  }
}
?>
