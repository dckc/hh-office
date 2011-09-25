<?
class tables_Client {
  function titleColumn(){
    return 'name';
  }

  function update_balance($id) {
    $res = df_query("
update hh_office.Client c
join Client_Balances cb
on cb.client_id = c.id
set balance_updated=current_timestamp,
c.recent = cb.recent,
c.client_paid = cb.client_paid,
c.insurance_paid = cb.insurance_paid,
c.balance = cb.balance
where c.id='$id'",
		    null, true);
    if ( !$res ) throw new Exception(mysql_error(df_db()));

    @mysql_free_result($res);
  }

  function block__before_charges_widget($params) {
    $record =& Dataface_Application::getInstance()->getRecord();
    $this->update_balance($record->val('id'));
    
  }
}
?>
