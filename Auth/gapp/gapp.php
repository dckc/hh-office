<?php
/* cribbed from cas.php

http://sourceforge.net/projects/dataface/files/xataface-cas/dataface-cas-0.1/dataface-cas-0.1.tar.gz
9ad8426bf6afc27445a073ae9057c88f  dataface-cas-0.1.tar.gz
 */

class dataface_modules_gapp {

  function showLoginPrompt(){
    require_once(dirname(dirname(__FILE__)).'/lib/GoogleOpenID.php');

    if ( isset( $_REQUEST['-action'] ) and $_REQUEST['-action'] == 'logout' ){
      session_destroy();

      $redirect = ( (isset($_REQUEST['-redirect'])
		     and !empty($_REQUEST['-redirect']) )
		    ? $_REQUEST['-redirect']
		    : $_SERVER['HOST_URI'].DATAFACE_SITE_HREF);
      header('Location: '.$redirect);
      exit;
    }

    if (!@$_SESSION['UserName']) {
      $app =& Dataface_Application::getInstance();

      if (!isset( $_REQUEST['-return'] )) {
	$ah = $this->loadAssociationHandle($app);

	$addr = (((!empty($s['HTTPS']) && $_SERVER['HTTPS']) ? "https://" : "http://") . $_SERVER['HTTP_HOST'] .
	      DATAFACE_SITE_HREF . '?-action=login&-return=1');
	//error_log('loging redirect: ' . $addr . "\n", 3, 'gapp.log');
	$googleLogin = GoogleOpenID::createRequest($addr, $ah, true);
	$googleLogin->redirect();
	exit;
      } else {
	$googleLogin = GoogleOpenID::getResponse();
	if($googleLogin->success()){
	  if ( ends_with($googleLogin->email(),
			 '@hopeharborkc.com')) {
	    $_SESSION['UserName'] = $googleLogin->email();

	    if ( isset( $_REQUEST['-redirect'] )
		 and !empty($_REQUEST['-redirect']) ){
	      $url = $_REQUEST['-redirect'];
	    } else if ( isset($_SESSION['--redirect']) ){
	      $url = $_SESSION['--redirect'];
	      unset($_SESSION['--redirect']);
	    } else {
	      $url = $app->url('');
	    }
	    // Now we forward to the homepage:
	    header('Location: '.$url.
		   '&--msg='.urlencode('You are now logged in'));
	    exit;
	  } else {
	    //trigger_error('how to handle wrong domain?', E_USER_ERROR);
	    session_destroy();
	    header('', true, 401);
	    exit('Not authorized: ' . $googleLogin->email());
	  }
	}
	trigger_error('unexpected login return', E_USER_ERROR);
      }
    }
  }

  function loadAssociationHandle($app) {
    if ( !isset($app->_conf['_auth']['association_handle_file']) ) {
      trigger_error("No association_handle_file was specified in the _auth section of the conf.ini file. Please supply the full path to a file writable by the web server.", E_USER_ERROR);
    }
    $apath = $app->_conf['_auth']['association_handle_file'];

    /* Docs say these handles last 2 weeks.
     Make sure ours is less than 1 week old. */
    $a_week = 7 * 24 * 60 * 60;
    if (time() - filemtime($apath) < $a_week) {
      $afh = fopen($apath, 'r');
      if ($afh) {
	$handle = fread($afh, filesize($apath));
	fclose($afh);
      } else {
	$handle = null;
      }
    }

    if (!$handle) {
      $association_handle = GoogleOpenID::getAssociationHandle();
  
      $afh = fopen($apath, "w");
      fwrite($afh, $association_handle);
      fclose($afh);
    }
  }


  function getLoggedInUsername(){
    if ( !@$_SESSION['UserName'] ) return null;
    return @$_SESSION['UserName'];	
  }
	
  /**
   * Returns the Dataface_Record for the currently logged in user.
   */
  function &getLoggedInUser(){
    static $record = 0;
    if ( $record === 0 ) {
      if ( @$_SESSION['UserName'] ) {
	//echo 'get logged in user for: '. $_SESSION['UserName'].'<br/>';
	$auth =& Dataface_AuthenticationTool::getInstance();

	$binding = array($auth->usernameColumn=>$_SESSION['UserName']);

	// got one in the database?
	$record = df_get_record($auth->usersTable, $binding);
	if (!$record) {
	  // no... synthesize one
	  $record = new Dataface_Record($auth->usersTable, $binding);
	}
      }
    }
    return $record;
  }
	
  function logout(){
      session_destroy();
  }
}
?>
