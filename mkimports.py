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

import MySQLdb   #@@@

# http://pypi.python.org/pypi/SQLAlchemy/0.7.2
# b84a26ae2e5de6f518d7069b29bf8f72
from sqlalchemy import create_engine, MetaData, Table, Column
from sqlalchemy import TEXT, VARCHAR, INTEGER
from sqlalchemy.schema import CreateTable

import hh_data1 as hh  # misnomer? should be dabble?


def main(argv):
    if '--zoho' in argv:
        d = argv[2]
        xe = xataface_engine()
        import_zoho(xe, d)
    elif '--dabble' in argv:
        sqdb = argv[2]
        de = create_engine('sqlite:///%s' % sqdb)
        xe = xataface_engine()
        import_dabble(de, xe)
    elif '--diagram' in argv:
        outf = argv[2]
        xe = xataface_engine()
        schema_diagram(xe, outf)
    else:
        print >> sys.stderr, __doc__
        exit(1)
    

def schema_diagram(xe, outf):
    from sqlalchemy import MetaData
    from sqlalchemy_schemadisplay import create_schema_graph

    metadata=MetaData()
    metadata.reflect(bind=xe)
    for tn, t in metadata.tables.iteritems():
        print "@@table: ", t
        for fk in t.foreign_keys:
            print "@@fk:", fk

    # create the pydot graph
    graph = create_schema_graph(metadata=metadata,
                                show_datatypes=False, # too big
                                show_indexes=False, # ditto for indexes
                                rankdir='LR',
                                concentrate=False # Don't join relation lines
                                )
    graph.write_svg(outf)


def import_dabble(dabble, xata, dabble_schema='dabbledb',
                  tables=('offices', 'officers'
                          'batches', 'clients',
                          'groups', 'sessions', 'visits')
                  ):
    meta = hh.meta

    for tn, t in list(meta.tables.iteritems()):
        print CreateTable(t, on='mysql')

    xata.execute('use %s' % dabble_schema)
    print "dropping: ", meta.tables.keys()
    meta.drop_all(bind=xata)
    print "creating: ", meta.tables.keys()
    meta.create_all(bind=xata)

    raise RuntimeError, '@@now copy the records...'


def import_zoho(ze, d):
    zcmeta = MetaData(ze)

    with transaction(ze) as do:
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
            t = with_cols(zcmeta, n, schema,
                          mysql_engine='InnoDB',
                          schema='zc')

            with transaction(ze) as do:
                t.create(bind=ze)

            print "created: ", n, schema

            rows = [dict(dict(zip(schema, [fix_cell(txt) for txt in row])),
                         pkey=None)
                    for row in r]

            print "@@rows: ", rows[:3]
            with transaction(ze) as do:
                do.execute(t.insert(n, schema), rows)
                                                               
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

      >>> xataface_engine() is None
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

      >>> xataface_connection() is None
      False

    '''
    opts = ConfigParser.SafeConfigParser()
    opts.read(ini)

    def opt(n):
        v = opts.get(section, n)
        return v[1:-1]  # strip ""s

    return MySQLdb.connect(opt('host'), opt('user'),
                           opt('password'), opt('name'))



def with_cols(meta, tn, cols, **kw):
    cols = [Column('pkey', INTEGER(), primary_key=True)] + [
        Column(n,
               TEXT() if ('note' in n.lower() or '_link' in n
                          or n == 'Approval') else VARCHAR(80))
        for n in cols]
    return Table(tn, meta, *tuple(cols), **kw)


def create_ddl(table_name, cols):
    r'''
    >>> ddl = create_ddl('products', ['id', 'size', 'color',
    ...                               'note', 'orders_link'])
    >>> print ddl  #doctest: +NORMALIZE_WHITESPACE
    CREATE TABLE products (
    	pkey INTEGER NOT NULL, 
    	id VARCHAR(80), 
    	size VARCHAR(80), 
    	color VARCHAR(80), 
    	note TEXT, 
    	orders_link TEXT, 
    	PRIMARY KEY (pkey)
    )


    '''
    t = with_cols(MetaData(), table_name, cols)
    return str(CreateTable(t))


def insert_dml(table_name, cols):
    r'''
      >>> dml = insert_dml('products', ('id', 'size', 'color'))
      >>> dml #doctest: +NORMALIZE_WHITESPACE
      'INSERT INTO products (pkey, id, size, color)
       VALUES (:pkey, :id, :size, :color)'

    '''
    t = with_cols(MetaData(), table_name, cols)
    return str(t.insert())


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
def transaction(e):
    '''Return a sqlalchemy transaction manager.

    see `Using Transactions`__
    __ http://www.sqlalchemy.org/docs/core/connections.html#using-transactions

    :param e: an engine
    '''
    conn = e.connect()
    trx = conn.begin()
    try:
        yield conn
    except IOError:
        trx.rollback()
        raise
    else:
        trx.commit()
    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    main(sys.argv)

