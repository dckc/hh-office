import datetime

import rlib  # http://rlib.sicompos.com/
             # 06b3e629c6f99a8b2fd1264f32db8f56  rlib-1.3.7.tar.gz

def run(report_def="report1.xml",
        hostname='localhost', username='hopeharborkc',
        password='satsep3', database='hh_office'):
    myreport = rlib.Rlib()
    print rlib.version
    dsn = "local_mysql"
    myreport.add_datasource_mysql(dsn,
                                  hostname, username, password, database)
    myreport.add_query_as(dsn, r'''
select g.id as group_id, g.name as `Group`
     , c.id as client_id, c.name as `Client`
     , date_format(s.session_date, '%Y-%m-%d') as `Session`
     , attend_n, charge, client_paid
     , insurance_paid, due
     , v.note
from zvisit as v
join zsession as s
  on v.session_id = s.id
join zgroup as g
  on s.group_id = g.id
join zclient c
  on v.client_id = c.id
order by g.name, c.name, s.session_date
    ''', 'attendance')
    myreport.add_report(report_def)
    myreport.set_output_format_from_text("pdf")
    myreport.set_output_encoding('UTF-8')
    myreport.add_parameter("report_date", datetime.date.today().isoformat())
    myreport.execute()
    print myreport.get_content_type_as_text()
    myreport.spool()

if __name__ == '__main__':
    run()
