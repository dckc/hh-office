import datetime

import rlib  # http://rlib.sicompos.com/
             # 06b3e629c6f99a8b2fd1264f32db8f56  rlib-1.3.7.tar.gz

def run(report_dml, report_def="report1.xml", report_name='report1',
        hostname='localhost', username='hopeharborkc',
        password='satsep3', database='hh_office'):
    myreport = rlib.Rlib()
    print rlib.version
    dsn = "local_mysql"
    myreport.add_datasource_mysql(dsn,
                                  hostname, username, password, database)
    myreport.add_query_as(dsn, report_dml, report_name)
    myreport.add_report(report_def)
    myreport.set_output_format_from_text("pdf")
    myreport.set_output_encoding('UTF-8')
    myreport.add_parameter("report_date", datetime.date.today().isoformat())
    myreport.execute()
    print myreport.get_content_type_as_text()
    myreport.spool()

if __name__ == '__main__':
    import sys
    sql_file, report_def_file = sys.argv[1:3]
    run(open(sql_file).read(), report_def_file)
