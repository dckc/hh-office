<?
class tables_Insurance extends Audited {

  function block__tables_menu_head () {
    $app =& Dataface_Application::getInstance();
    $key = $app->_conf['_database']['report_key'];
    echo "<ul class='report_menu'>
            <li><a href='print_report/ins_claims.xml?key=$key'
                target='_new'>Insurance Claims</a></li>
         </ul>";
  }

}
