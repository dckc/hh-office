'''Import data from Zoho CSV backups

Usage:

 1. set up conf.ini per xataface conventions
 % python mkimports.py --zoho dir-of-csv-files/
 % python mkimports.py --dabble dir-of-csv-files/
 
'''

import os
import csv
import ConfigParser
from contextlib import contextmanager

# http://pypi.python.org/pypi/SQLAlchemy/0.7.2
# b84a26ae2e5de6f518d7069b29bf8f72
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.schema import CreateTable

import hh_data1 as hh


def main(argv):
    if '--zoho' in argv:
        d = argv[2]
        c = xataface_connection()
        import_zoho(c, d)
    elif '--dabble' in argv:
        sqdb = argv[2]
        de = create_engine('sqlite:///%s' % sqdb)
        xe = xataface_engine()
        import_dabble(de, xe)
    else:
        print >> sys.stderr, __doc__
        exit(1)
    

def import_dabble(dabble, xata, dabble_schema='dabbledb',
                  tables=('offices', 'officers'
                          'batches', 'clients',
                          'groups', 'sessions', 'visits')
                  ):
    meta = hh.meta

    for tn, t in list(meta.tables.iteritems()):
        print CreateTable(t, on='mysql')

    print "creating: ", meta.tables.keys()
    xata.execute('use %s' % dabble_schema)
    meta.create_all(bind=xata)

    raise RuntimeError, '@@now copy the records...'


def import_zoho(conn, d):
    with transaction(conn) as do:
        do.execute('drop database if exists zc');
        do.execute('create database zc'
                   ' character set utf8'
                   ' collate utf8_bin');

    for fn in sorted(os.listdir(d)):
        if fn.endswith('.csv'):
            n = fn[:-len('.csv')]
            r = csv.reader(open(os.path.join(d, fn)))
            schema = [colname + '_' if colname.lower() == 'group' else colname
                      for colname in r.next()]

            with transaction(conn) as do:
                do.execute('use zc')
                do.execute(create_ddl(n, schema))
            print "created: ", n, schema

            rows = [[None] + [fix_cell(txt) for txt in row]
                    for row in r]

            with transaction(conn) as do:
                do.executemany(insert_dml(n, schema), rows)
                                                               
            print "inserted %d rows." % len(rows)

            print


def fix_cell(txt):
    if txt == 'zcnull':
        return None
    else:
        return txt.replace('zccomma', ',').replace('zcnewline', '\n')


def xataface_engine(ini='conf.ini', section='_database'):
    '''Make sqlalchemy engine following xataface conventions.

    @param ini: `conf.ini`, per `xataface docs`__
    @param section: `_database`, per xataface

    __ http://xataface.com/wiki/conf.ini_file

    .. todo: separate this integration test from unit/function tests.

      >>> mysql_connection() is None
      False

    '''
    opts = ConfigParser.SafeConfigParser()
    opts.read(ini)

    def opt(n):
        v = opts.get(section, n)
        return v[1:-1]  # strip ""s

    # per http://www.sqlalchemy.org/docs/dialects/mysql.html#module-sqlalchemy.dialects.mysql.mysqldb
    return create_engine('mysql+mysqldb://%s:%s@%s/%s' % (
        opt('user'), opt('password'), opt('host'), opt('name'))
                         , pool_recycle=3600)


def xataface_connection(ini='conf.ini', section='_database'):
    '''Open mysql connection following xataface conventions.

    @param ini: `conf.ini`, per `xataface docs`__
    @param section: `_database`, per xataface

    __ http://xataface.com/wiki/conf.ini_file

    .. todo: separate this integration test from unit/function tests.

      >>> mysql_connection() is None
      False

    '''
    opts = ConfigParser.SafeConfigParser()
    opts.read(ini)

    def opt(n):
        v = opts.get(section, n)
        return v[1:-1]  # strip ""s

    return MySQLdb.connect(opt('host'), opt('user'),
                           opt('password'), opt('name'))


def create_ddl(table_name, cols):
    '''
    >>> print create_ddl('products', ['id', 'size', 'color',
    ...                               'note', 'orders_link'])
    create table products (pkey int auto_increment primary key,
       id varchar(80),
       size varchar(80),
       color varchar(80),
       note text,
       orders_link text)

    '''
    return 'create table %s (%s,\n   %s)\n%s' % (
        table_name,
        'pkey int auto_increment primary key',
        ',\n   '.join(['%s %s' % (
            n, 'text' if ('note' in n.lower() or '_link' in n
                          or n == 'Approval') else 'varchar(80)')
                       for n in cols]),
        'character set utf8 collate utf8_bin')


def insert_dml(table_name, cols):
    r'''
      >>> insert_dml('products', ('id', 'size', 'color'))
      'insert into products values (%s, %s, %s, %s)'
    '''
    return 'insert into %s values (%s)' % (
        table_name, ', '.join(["%s"] + ["%s" for _ in cols]))


def load_data_dummy():
    sql=  r"""LOAD DATA LOCAL INFILE  '%s'
              INTO TABLE  `%s`
              CHARACTER SET binary
              FIELDS TERMINATED BY  ','
              ENCLOSED BY  '"'
              ESCAPED BY  '\\'
              LINES TERMINATED BY  '\n' """

    #" '



@contextmanager
def transaction(conn):
    '''Return an Oracle database cursor manager.

    :param conn: an Oracle connection
    '''
    c = conn.cursor()
    try:
        yield c
    except IOError:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        c.close()


if __name__ == '__main__':
    import sys
    main(sys.argv)

