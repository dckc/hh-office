
import os
import csv
from contextlib import contextmanager

sql=  r"""LOAD DATA LOCAL INFILE  '%s'
          INTO TABLE  `%s`
          CHARACTER SET binary
          FIELDS TERMINATED BY  ','
          ENCLOSED BY  '"'
          ESCAPED BY  '\\'
          LINES TERMINATED BY  '\n' """

#" '
         
def import_all(conn, d,
               extra_columns=('Added_User',
                              'Added_Time',
                              'Modified_User',
                              'Added_User_IP_Address',
                              'Modified_User_IP_Address')):
    with transaction(conn) as do:
        do.execute('drop database if exists hh_office');
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

            if n.startswith('zcfrm') and False:
                for col in extra_columns:
                    with transaction(conn) as do:
                        do.execute('alter table %s drop %s' % (n, col))

                print "dropped extra columns"
            print


def fix_cell(txt):
    if txt == 'zcnull':
        return None
    else:
        return txt.replace('zccomma', ',').replace('zcnewline', '\n')


def mysql_connect(user='hopeharborkc', p='satsep3'):
    import MySQLdb # http://mysql-python.sourceforge.net/MySQLdb.html#mysqldb
    return MySQLdb.connect(user=user, passwd=p)


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
    d = sys.argv[1]
    c = mysql_connect()
    import_all(c, d)

