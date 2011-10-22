<?php
/**
 * File: index.php
 * Description:
 * -------------
 *
 * This is an entry file for this Dataface Application.  To use your application
 * simply point your web browser to this file.
 */

// Report simple running errors
error_reporting(E_ERROR | E_PARSE);

$time = microtime(true);
	// use the timer to time how long it takes to generate a page
require_once '/home/dckc/hh-office.dreamhosters.com/hh-office/lib/xataface-1.3rc6/dataface-public-api.php';
	// include the initialization file
df_init(__FILE__, '/hh-office/lib/xataface-1.3rc6');
	// initialize the site

$app =& Dataface_Application::getInstance();
	// get an application instance and perform initialization
$app->display();
	// display the application


$time = microtime(true) - $time;
echo "<!--Execution Time: $time-->";
?>