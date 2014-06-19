<?
class tables_Therapist extends Audited {
  function block__tables_menu_head () {
    $app =& Dataface_Application::getInstance();
    $key = $app->_conf['_database']['report_key'];
    echo "<ul class='report_menu'>
           <li><a href='print_report/income_by_therapist?key=$key'
	          target='_new'>Income By Therapist</a></li>
          </ul>";
  }
}
