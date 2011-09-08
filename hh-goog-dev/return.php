<?php
require_once('GoogleOpenID.php');
$googleLogin = GoogleOpenID::getResponse();
if($googleLogin->success()){
  $user_id = $googleLogin->identity();
  $user_email = $googleLogin->email();
 }
echo "usr_id: " . $user_id;
echo "<br />";
echo "email: " . $user_email;
?>
