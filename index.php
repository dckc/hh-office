<?php
/**
 * File: index.php
 * Description:
 * -------------
 *
 * This is an entry file for this Dataface Application.  To use your application
 * simply point your web browser to this file.
 */

require_once 'hh_conf.php';

/* Use Strict-Transport-Security (STS) to force the use of SSL.
 * ack: Nov 2010 http://www.php.net/manual/en/reserved.variables.server.php#100877
 */
if ($use_sts && isset($_SERVER['HTTPS'])) {
  header('Strict-Transport-Security: max-age=500');
} elseif ($use_sts && !isset($_SERVER['HTTPS'])) {
  header('Status-Code: 301');
  header('Location: https://'.$_SERVER["HTTP_HOST"].$_SERVER['REQUEST_URI']);
  exit;
}

$time = microtime(true);
	// use the timer to time how long it takes to generate a page

require_once 'lib/xataface-1.3rc6/dataface-public-api.php';
	// include the initialization file
df_init(__FILE__, '/hh-office/lib/xataface-1.3rc6');
	// initialize the site

$app =& Dataface_Application::getInstance();
	// get an application instance and perform initialization
$app->display();
	// display the application


$time = microtime(true) - $time;
//interferes with auto-complete
//echo "<!--Execution Time: $time-->";
?>
