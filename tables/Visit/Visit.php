<?
class tables_Visit extends Audited{
  function attend_n__default () {
    return 1;
  }


  function block__tables_menu_head () {
    $app =& Dataface_Application::getInstance();
    $key = $app->_conf['_database']['report_key'];
    echo "<ul class='report_menu'>
            <li><a href='export_claims?key=$key'
                target='_new'>Insurance Claims</a></li>
         </ul>";
  }

  function block__after_Client_id_widget() {
    $client_name = '';
    $app =& Dataface_Application::getInstance();
    $query = $app->getQuery();
    if ($query['-action'] == 'edit' or $query['-action'] == 'browse') {
      $record =& $app->getRecord();
      $client = $record->getRelatedRecord('client');
      $client_name = $client->val('name');
    }

    echo "<input id='Client_id_ac' value='$client_name' tabindex='3'/>\n";

    echo '<a href="#" onclick="return false" id="Client_id-other">Other..</a>';

    echo "<script src='av/jqac/jquery.autocomplete.js'></script>";
    echo "<script type='text/javascript'>
\$('#Client_id').hide();
\$('#Client_id_ac').autocomplete({
   url: 'index.php',
   paramName: '-search',
   selectFirst: true,
   extraParams: {'-action': 'client_data',
                '-table': 'Client',
                '-value': 'id',
                '-text': 'name'},
   onItemSelect: function(item) {
     \$('#Client_id').val(item.data);
     }
});
</script>";

    // copy-and-paste KLUDGE? but that's what xataface code seems to do.
    echo '
<script type="text/javascript" src="'.DATAFACE_URL.'/js/jquery-ui-1.7.2.custom.min.js"></script>
<script type="text/javascript" src="'.DATAFACE_URL.'/js/RecordDialog/RecordDialog.js"></script>
<script>
  $("head").append("<link rel=\"stylesheet\" type=\"text/css\" href=\""+DATAFACE_URL+"/css/smoothness/jquery-ui-1.7.2.custom.css\"/>");
  jQuery(document).ready(function($){
      $("#Client_id-other").each(function(){
	  var tablename = "Client";
	  var valfld = "name";
	  var keyfld = "id";
	  var fieldname = "Client_id";
	  var btn = this;
	  $(this).RecordDialog({
	      table: tablename,
	      callback: function(data){
		  var key = data[keyfld];
		  var val = data[valfld];
		  $("#"+fieldname).val(key);
		  $("#"+fieldname+"_ac").val(val);
	      }
	  });
      });
  });
</script>';

  }

  function block__after_claim_uid_widget () {
    $app =& Dataface_Application::getInstance();
    $record =& $app->getRecord();
    $trace_no = $record->val('claim_uid');
    if ($trace_no) {
      echo "<div><a target='_new'
          href='https://sfreeclaims.anvicare.com/docs/viewonehcfa.asp?trace_no=$trace_no'
          >CLAIM FORM HCFA-1500 at FreeClaims</a></div>";
    }
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

  function cpt__default () {
    $app =& Dataface_Application::getInstance();
    $record =& $app->getRecord();
    $gid = $record->val('Group_id');
    if ($gid) {
      $res = df_query("select cpt from `Group` g
                         where g.id = $gid
                         ", null, true);
      if ( !$res ) throw new Exception(mysql_error(df_db()));
      $cpt = $res[0]['cpt'];
      return $cpt;
    } else {
      return null;
    }
  }

  function block__after_main_section() {
    echo '<script type="text/javascript">
(function () {
    $("form[method=\"post\"] input[type=\"submit\"]").each(function() {
            var save = $(this);
            save.attr("tabindex", 11); //HARDCODED
            save.attr("accesskey", "S");
    });
//alert("set tab index on " + tabindex + " fields");

    // no tabbing through links nor the search form
    $("a, .search_form input").each(function() {
            var a = $(this);
            a.attr("tabindex", -1);
    });

})();
</script>
';
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
