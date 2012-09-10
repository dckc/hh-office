<?
class tables_Group extends Audited {

  function block__tables_menu_head () {
    $app =& Dataface_Application::getInstance();
    $key = $app->_conf['_database']['report_key'];
    echo "<ul class='report_menu'>
            <li><a href='print_report/attendance_by_group?key=$key'
                target='_new'>Attendance by Group</a></li>
            <li><a href='print_report/last_30?key=$key'
                target='_new'>30 Day Attendance by Group</a>
            <li><a href='print_report/last_30_blank?key=$key'
                target='_new'>30 Day ... w/blank</a>
            </li>
            <li><a href='print_report/evaluations?key=$key'
                target='_new'>Evaluations</a></li>
           <li><a href='print_report/cwip-yr?key=$key'
                  target='_new'>CWIP</a></li>
           <li><a href='print_report/monitoring?key=$key'
                  target='_new'>Monitoring</a></li>
         </ul>";
  }

}
