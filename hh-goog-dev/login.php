<?php
require_once('GoogleOpenID.php');
$apath = "/u/2/connolly/dm93.org/htdocs/hh-goog-dev/assoc/assoc1";
$afh = fopen($apath);
$association_handle = fread($afh, filesize($apath));
if (!$association_handle) {
  fclose($afh);
  $afh = fopen($apath, "w");

  //fetch an association handle
  $association_handle = GoogleOpenID::getAssociationHandle();
  
  fwrite($afh, $association_handle);
 }

$googleLogin = GoogleOpenID::createRequest("/hh-goog-dev/return.php", $association_handle, true);
$googleLogin->redirect();
?>
