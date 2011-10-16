<?
class tables_Visit extends Audited{
  function attend_n__default () {
    return 1;
  }

  function charge__default () {
    $app =& Dataface_Application::getInstance();
    $record =& $app->getRecord();
    $gid = $record->val('Group_id');
    if ($gid) {
      $res = df_query("select rate from `Group` g
                         where g.id = $gid
                         ", null, true);
      if ( !$res ) throw new Exception(mysql_error(df_db()));
      $rate = $res[0]['rate'];
      return $rate;
    } else {
      return null;
    }
  }

  function afterInsert ($record) {
    $vid = $record->val('id');
    /* If a dormant client returns, set the billing_cutoff per session. */
    $res = df_query("
     update Client c
       join Visit v on v.Client_id = c.id and v.id = $vid
       join `Session` s on v.Session_id = s.id
     set c.billing_cutoff =
     case when c.billing_cutoff is null
      then s.session_date
      else c.billing_cutoff end,
     c.recent=greatest(s.session_date, c.recent)");
    $client = Dataface_Table::loadTable('Client');
    $client->getDelegate()->update_balance($record->val('Client_id'));
  }

  function afterDelete ($record) {
    $cid = $record->getRelatedRecord('client')->val('id');
    $client = Dataface_Table::loadTable('Client');
    $client->getDelegate()->update_balance($cid);
  }

}
