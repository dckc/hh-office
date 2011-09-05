<?php
class actions_hello {
    function handle(&$params){
      $app =& Dataface_Application::getInstance();

      $body = "<br /><br />";

      $hd1 = query_result($app->db(), "
select g.id as group_id, g.name as `Group`
from zgroup g
order by g.name");

      $hd2 = query_result($app->db(), "
select distinct g.id as group_id, g.name as `Group`
     , c.id as client_id, c.name as `Client`
     , null
     , sum(v.attend_n) as attend_n, sum(v.charge) as `Charges`, sum(v.client_paid) as `Client Paid`
     , sum(case when v.insurance_paid is null then 0 else v.insurance_paid end) as insurance_paid, sum(v.due) as due
from zvisit v
  join zsession s on v.session_id = s.id
  join zgroup g on s.group_id = g.id
  join zclient c on v.client_id = c.id
group by g.id, c.id
order by g.name, c.name");

      $headings = array();
      $summary = array();
      $group_idx = 0;
      foreach ($hd2 as $client_row) {
	if ($client_row['group_id'] != $hd1[$group_idx]['group_id']) {
	  $group_idx++;
	}
	$headings[] = array(array_slice($hd1[$group_idx], 1),
			    array_slice($client_row, 3, 1));
	$summary[] = array_slice($client_row, 4);
      }

      $data = query_result($app->db(), "
select g.id as group_id, g.name as `Group`
     , c.id as client_id, c.name as `Client`
     , date_format(s.session_date, '%b %d \'%y') as `Session`
     , attend_n, charge, client_paid
     , insurance_paid, due
from zvisit as v
join zsession as s
  on v.session_id = s.id
join zgroup as g
  on s.group_id = g.id
join zclient c
  on v.client_id = c.id
order by g.name, c.name
");

      $datagroups = array();
      $idx = 0;
      $detail_rows = array();
      foreach ($data as $detail) {
	#echo "@@hd", $hd2[$idx]['Group'], $hd2[$idx]['Client'], "<br/>";
	#echo "@@dt", $detail['Group'], $detail['Client'], $detail['Session'],"<br />\n";
	if ($detail['client_id'] != $hd2[$idx]['client_id']
	    || $detail['group_id'] != $hd2[$idx]['group_id']) {
	  #echo "@@detail rows:", count($detail_rows), "<br/>";
	  $datagroups[] = $detail_rows;
	  #echo "@@datagroups:", count($datagroups), "<br/>";
	  #echo "@@size of prev datagroup:", count($datagroups[$idx-1]), "<br/>";
	  $detail_rows = array();
	  $idx ++;
	}
	$detail_rows[] = array_slice($detail, 4);
      }
      $datagroups[] = $detail_rows;

      df_display(array('headings'=>$headings,
		       'data'=>$datagroups,
		       'summary' => $summary),
		 'report3.html');
    }

  }

function query_result($db, $sql) {
  $result = mysql_query($sql, $db);
  if ( !$result ) throw new Exception(mysql_error(df_db()));
  
  while($row = mysql_fetch_assoc($result))
    {
      $data[] = $row;
    }
  mysql_free_result($result);
  
  return $data;
}

?>
