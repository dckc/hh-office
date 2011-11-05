<?
class tables_Group extends Audited {

  function block__tables_menu_head () {
    $app =& Dataface_Application::getInstance();
    $key = $app->_conf['_database']['report_key'];
    echo "<ul class='report_menu'>
            <li><a href='print_report/attendance_by_group?key=$key'
                target='_new'>Attendance by Group</a></li>
         </ul>";
  }

}
