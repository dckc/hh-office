<?
class tables_Client {
  function titleColumn(){
    return 'name';
  }

  function update_balances($id=null) {
    $dml = "
update hh_office.Client c
join Client_Balances cb
on cb.client_id = c.id
set balance_updated=current_timestamp,
c.recent = cb.recent,
c.charges = cb.charges,
c.client_paid = cb.client_paid,
c.insurance_paid = cb.insurance_paid,
c.balance = cb.balance";

    if ($id) {
      $dml = $dml . " where c.id='$id'";
    }

    $res = df_query($dml, null, true);
    if ( !$res ) throw new Exception(mysql_error(df_db()));

    @mysql_free_result($res);
  }

  function update_balance($id=0) {
    # TODO: consider passing in the record instead.
    if ($id == 0) {
      $record =& Dataface_Application::getInstance()->getRecord();
      $id = $record->val('id');
    }

    $this->update_balances($id);
  }

  function after_action_new () {
    $this->update_balance();
  }

  function after_action_edit () {
    $this->update_balance();
  }

  function afterRemoveRelatedRecord () {
    $this->update_balance();
  }
}
?>
