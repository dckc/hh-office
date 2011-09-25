<?
class tables_Client {
  function titleColumn(){
    return 'name';
  }

  function update_balance($id) {
    $res = df_query("
update hh_office.Account
set balance_updated=current_timestamp,
charges = (select sum(v.charge)
  from hh_office.Attendance_all v
  where client_id=$id
    and session_date >= opened),
client_paid = (select sum(v.client_paid)
  from hh_office.Attendance_all v
  where client_id=$id
    and session_date >= opened),
insurance_paid = (select sum(case when v.insurance_paid is null then 0
                           else v.insurance_paid end)
  from hh_office.Attendance_all v
  where client_id=$id
    and session_date >= opened),
balance = (select sum(v.due)
  from hh_office.Attendance_all v
  where client_id=$id
    and session_date >= opened)
where Client_id=$id",
		    null, true);
    if ( !$res ) throw new Exception(mysql_error(df_db()));
  }

  function block__before_Visits_row($params) {
    $record =& Dataface_Application::getInstance()->getRecord();
    $id = $record->val('id');

    $this->update_balance($id);
    $res = df_query("select balance as b
                     from hh_office.Account where Client_id=$id",
		    null, true);
    if ( !$res ) throw new Exception(mysql_error(df_db()));

    $row = $res[0];
    $b = $row['b'];
    echo "<h4>Balance: $$b</h4>";
    
    @mysql_free_result($res);
  }
}
?>
