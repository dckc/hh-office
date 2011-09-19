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
from sqlalchemy import create_engine, MetaData, Table, Column
from sqlalchemy import TEXT, VARCHAR, INTEGER
from sqlalchemy.schema import CreateTable


def main(argv):
    if '--zoho' in argv:
        d = argv[2]
        xe = xataface_engine()
        import_csvdir(xe, d, 'zc', zoho_fixup)
    elif '--dabble' in argv:
        d = argv[2]
        xe = xataface_engine()
        import_csvdir(xe, d, 'dabbledb', dabble_fixup)
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


def import_csvdir(engine, d, db, fixup):
    meta = MetaData(engine)

    with transaction(engine) as do:
        do.execute('drop database if exists %s' % db);
        do.execute('create database %s'
                   ' character set utf8'
                   ' collate utf8_bin' % db);

    for fn in sorted(os.listdir(d)):
        if not fn.endswith('.csv'):
            continue
        n = fn[:-len('.csv')]
        r = csv.reader(open(os.path.join(d, fn)))
        schema = r.next()
        t = with_cols(meta, n, schema,
                      schema=db)

        with transaction(engine) as do:
            t.create(bind=engine)

            print "created: ", n, schema, CreateTable(t, bind=engine)
            import sys
            sys.stdout.flush()

            rows = fixup(schema, r)
            if rows:
                do.execute(t.insert(), rows)
                print "inserted %d rows." % len(rows)

        print


def dabble_fixup(schema, r):
    '''oops... I guess I could just use LOAD DATA INFILE for dabble.
    '''
    return [dict(zip(schema, row))
            for row in r]


def zoho_fixup(schema, r):
    return [dict(zip(schema, [fix_cell(txt) for txt in row]))
            for row in r]


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
    return create_engine('mysql+mysqldb://%s:%s@%s/%s?charset=utf8' % (
        opt('user'), opt('password'), opt('host'), opt('name'))
                         , pool_recycle=3600)


def with_cols(meta, tn, cols, field_size=80, **kw):
    cols = [Column('pkey', INTEGER(), primary_key=True)] + [
        Column(n,
               TEXT() if ('note' in n.lower() or '_link' in n
                          or n == 'Approval') else VARCHAR(field_size))
        for n in cols]
    return Table(tn, meta, *tuple(cols), **kw)


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

