<?
class tables_Client {
  function titleColumn(){
    return 'name';
  }

  function block__before_record_content () {
    $app =& Dataface_Application::getInstance();
    $record =& $app->getRecord();
    $res = df_query("select cutoff from Batch where name='current'",
		    null, true);
    if ( !$res ) throw new Exception(mysql_error(df_db()));
    $recent = $record->strval('recent');
    $cutoff = $res[0]['cutoff'];
    if ($recent < $cutoff) {
      echo "<p class='error'>Most recent visit ($recent) is before current batch cutoff ($cutoff). Current billing info is not available.</p>";
    }
  }

  function update_balances($id=null) {
    $dml = "
update hh_office.Client c
left join Client_Balances cb
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


    error_log("DEBUG: updating balances with id = $id");

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
