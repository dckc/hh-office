<?
class tables_Client {
  function titleColumn(){
    return 'name';
  }

  function block__before_Visits_row($params) {
    $record =& Dataface_Application::getInstance()->getRecord();
    $id = $record->val('id');

    $res = df_query("select sum(charge - client_paid -
      case when insurance_paid is null then 0 else v.insurance_paid end
                               ) as b
                     from hh_office.Visit v where v.Client_id = $id",
		    null, true);
    if ( !$res ) throw new Exception(mysql_error(df_db()));

    $row = $res[0];
    $b = $row['b'];
    echo "<h4>Balance: $$b</h4>";
    
    @mysql_free_result($res);
  }
}
?>
