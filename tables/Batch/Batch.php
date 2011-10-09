<?
class tables_Batch extends Audited {
  /*TODO: this is too obscure; move it to a POST button action somewhere. */
  function afterSave ($record) {
    $client = Dataface_Table::loadTable('Client');
    $client->getDelegate()->update_balances();
  }
}
