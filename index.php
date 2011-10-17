<?php
/**
 * File: index.php
 * Description:
 * -------------
 *
 * This is an entry file for this Dataface Application.  To use your application
 * simply point your web browser to this file.
 */
$time = microtime(true);
	// use the timer to time how long it takes to generate a page
require_once '/usr/local/src/xataface-1.3rc6/dataface-public-api.php';
	// include the initialization file
df_init(__FILE__, 'http://pav.local/xataface-1.3rc6');
	// initialize the site

$app =& Dataface_Application::getInstance();
	// get an application instance and perform initialization
$app->display();
	// display the application


$time = microtime(true) - $time;
//interferes with auto-complete
//echo "<!--Execution Time: $time-->";
?>