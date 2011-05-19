
from contextlib import contextmanager
from urllib import urlencode
from urllib2 import urlopen
import StringIO
import csv
import getpass
import json
import os
import pprint
import re
import sqlite3
import sys

from lxml import etree


def main(argv):
    if '--prepare-db' in argv:
        db, bak = argv[2:4]
        prepare_db(db, bak)
    elif '--load-basics' in argv:
        db, username = argv[2:4]

        conn = sqlite3.connect(db)

        def pw_cb():
            return getpass.getpass('Password for %s: ' % username)

        hz = HH_Zoho(conn, username, pw_cb, None)

        hz.load_basics()

    elif '--truncate' in argv:
        form = argv[2]
        hz = HH_Zoho(None, None, None, None)  # assume we have a ticket
        print >> sys.stderr, hz.truncate(form)

    elif '--load-visits' in argv:
        db = argv[2]
        conn = sqlite3.connect(db)
        hz = HH_Zoho(conn, None, None, None)  # assume we have a ticket
        hz.load_clients()
        hz.load_sessions()
        hz.load_visits()


def prepare_db(db, bak, init='hh_data.sql', fixup='hh_fixup.sql'):
    conn = sqlite3.connect(db)

    print >> sys.stderr, 'running script:', init
    conn.executescript(open(init).read())

    for table in ('Batch', 'Office', 'Progressnote',
                  'Client', 'Group', 'Officer',
                  'Session', 'Visit'):
        with transaction(conn) as work:
            print >> sys.stderr, "importing: ", table
            import_csv(work, os.path.join(bak, '%s.csv' % table), table)

    print >> sys.stderr, 'running script:', fixup
    conn.executescript(open(fixup).read())


class ZohoAPI(object):
    def __init__(self, login_id, password_cb):
        # violates the "constructors never fail" M3 convention
        self._ticket = self._get_ticket(login_id, password_cb)
        self._apikey = self._get_apikey()

    def _get_ticket(self, login_id, password_cb,
                    ticket_file=',zoho_ticket',
                    api_addr='https://accounts.zoho.com/login',
                    servicename='ZohoCreator'):
        # cf https://api.creator.zoho.com/Creator-API-Prerequisites-Generate-a-Ticket.html
        try:
            body = open(ticket_file).read()
        except IOError:
            params = {'LOGIN_ID': login_id,
                      'PASSWORD': password_cb(),
                      'FROM_AGENT': 'true',
                      'servicename': servicename,
                      'submit': 'Generate Ticket'}
            print >> sys.stderr, 'getting ticket...'
            ans = urlopen(api_addr, urlencode(params))
            body = ans.read()
            open(ticket_file, "w").write(body)
        return [v for n, v in
                [parts for parts in
                 [l.split('=', 1) for l in body.split('\n')]
                 if len(parts) == 2]
                if n == 'TICKET'][0]

    def _get_apikey(self,
                    api_key_file=',zoho_api_key'):
        return open(api_key_file).read().strip()

    def form_fields(self, app, form,
                    url='http://creator.zoho.com/api/%(format)s/%(applicationName)s/%(formName)s/fields/apikey=%(apikey)s&ticket=%(ticket)s'):
        # This worked to test API key/ticket usage.
        # print json.dumps(hz.form_fields(hz.app, 'group'),
        #                  sort_keys=True, indent=4)

        print >> sys.stderr, 'getting form fields...'
        ans = urlopen(url % dict(format='json',
                                 applicationName=app,
                                 formName=form,
                                 apikey=self._apikey,
                                 ticket=self._ticket))
        return json.loads(ans.read())

    def view_records(self, app, form, criteria, reloperator, columns,
                     url='http://creator.zoho.com/api/xml/read'):
        e = self._where(None, app, form, criteria, reloperator)
        #print >> sys.stderr, etree.tostring(e, pretty_print=True)
        print >> sys.stderr, 'view %s...' % form
        ans = urlopen(url,
                     urlencode(dict(apikey=self._apikey,
                                    ticket=self._ticket,
                                    XMLString=etree.tostring(e))))
        doc = etree.parse(ans)
        for err in doc.xpath('//response/form'
                             '/status[text() != "Success"]'):
            print >> sys.stderr, etree.tostring(err, pretty_print=True)
        #print >> sys.stderr, etree.tostring(doc, pretty_print=True)
        found = doc.xpath('//response/form/records/record')
        print >> sys.stderr, 'view got: %s x %d' % (form, len(found))
        return [
            [e_record.xpath('column[@name="%s"]/value/text()' % col)[0]
             for col in columns]
            for e_record in found]

    def add_records(self, app, form, columns, rows, chunk_size=200):
        done = 0
        while done < len(rows):
            print >> sys.stderr, '%s: %d of %d' % (form, done, len(rows))
            chunk = self._add_records(app, form, columns,
                                      rows[done:done + chunk_size])
            print >> sys.stderr, 'added %d in %s.' % (len(chunk), form)
            yield chunk
            done += chunk_size

    def _add_records(self, app, form, columns, rows,
                    url='http://creator.zoho.com/api/xml/write'):
        e = etree.Element('ZohoCreator')
        sub = etree.SubElement
        e_app = sub(sub(e, 'applicationlist'), 'application', name=app)
        e_form = sub(sub(e_app, 'formlist'), 'form', name=form)
        for row in rows:
            e_add = sub(e_form, 'add')
            for n in columns:
                # watch out for:
                # File "apihelpers.pxi", line 1242, in lxml.etree._utf8 (src/lxml/lxml.etree.c:19848)
                # ValueError: All strings must be XML compatible: Unicode or ASCII, no NULL bytes
                if row[n]:
                    sub(sub(e_add, 'field', name=n),
                        'value').text = unicode(row[n])  # allow integers
        print >> sys.stderr, 'add...', form, columns, rows[0]
        #print >>sys.stderr, etree.tostring(e, pretty_print=True)
        ans = urlopen(url,
                      urlencode(dict(apikey=self._apikey,
                                     ticket=self._ticket,
                                     XMLString=etree.tostring(e))))
        doc = etree.parse(ans)
        #print >> sys.stderr, etree.tostring(doc, pretty_print=True)
        for err in doc.xpath('//response/result/form'
                             '/add[status/text() != "Success"]'):
            print >> sys.stderr, etree.tostring(err, pretty_print=True)
        return doc.xpath('//response/result/form'
                         '/add[status/text()="Success"]/values')

    def delete(self, app, form, criteria, reloperator,
                   url='http://creator.zoho.com/api/xml/write'):
        e = self._where('delete', app, form, criteria, reloperator)
        print >> sys.stderr, '@@delete:', etree.tostring(e, pretty_print=True)
        print >> sys.stderr, 'delete %s...' % form
        ans = urlopen(url,
                     urlencode(dict(apikey=self._apikey,
                                    ticket=self._ticket,
                                    XMLString=etree.tostring(e))))
        return ans.read()

    def _where(self, op, app, form, criteria, reloperator):
        e = etree.Element('ZohoCreator')
        sub = etree.SubElement
        if op:
            e_app = sub(sub(e, 'applicationlist'), 'application', name=app)
            e_form = sub(sub(e_app, 'formlist'), 'form', name=form)
            e_crit = sub(sub(e_form, op), 'criteria')
        else:
            e_app = sub(e, 'application', name=app)
            e_form = sub(e_app, 'form', name=form)
            e_crit = sub(e_form, 'criteria')
        first = True
        for n, op, v in criteria:
            if not first:
                sub(e_crit, 'reloperator').text = reloperator
            sub(e_crit, 'field', name=n, compOperator=op, value=v)
        return e


class HH_Zoho(ZohoAPI):
    app = 'hope-harbor'

    def __init__(self, conn, login_id, password_cb, backup_dir):
        self._dir = backup_dir
        self._conn = conn
        ZohoAPI.__init__(self, login_id, password_cb)

    def load_basics(self):
        self.load_offices()
        self.load_officers()
        self.load_groups()

    def load_groups(self):
        dml = '''select id as id_dabble, name as Name, rate, Eval from groups'''
        cols, records = self._query(dml)
        self.truncate('group')
        return sum(len(r)
                   for r in self.add_records(self.app, 'group', cols, records))

    def load_clients(self):
        dml = '''select id as id_dabble, name as Name
                     , ins as Ins, approval as Approval
                     , DX, note as Note, officer as officer_dabble, DOB
                     , address, phone, batch from current_clients'''
        cols, records = self._query(dml)
        self.truncate('client')
        return sum(len(r) for r in
                   self.add_records(self.app, 'client', cols, records))

    def load_sessions(self):
        dml = '''select id as id_dabble, date as date_field
                     , group_id as group_dabble, time as Time
                     , therapist as Therapist from current_sessions'''
        cols, records = self._query(dml)
        self.truncate('session')
        return sum(len(r) for r in
                   self.add_records(self.app, 'session', cols, records))

    def load_visits(self, skip_past='Fetter, Jared'):
        dummy, client_records = self._query(
            "select id, name from current_clients "
            "where name > ? "
            "order by name", [skip_past])

        dml = '''select session as session_dabble
                     , client as client_dabble, attend as Attend
                     , note, client_pd, bill_date, check_date, ins_paid
                from current_visits where client = ?'''

        self.truncate('visit')
        tot = 0
        for who in client_records:
            print >> sys.stderr, "load visits for: ", who['name'].encode('utf-8')
            cols, records = self._query(dml, [who['id']])
            tot += sum(len(r) for r in
                       self.add_records(self.app, 'visit', cols, records))
        return tot

    def truncate(self, form):
        return self.delete(self.app, form,
                           [('ID', 'NotEqual', '0')], 'AND')

    def load_offices(self):
        dml = '''select id as id_dabble
                              , name as Name
                              , fax, address, notes from offices'''
        cols, records = self._query(dml)
        records = [dict(rec, address=rec['address'].replace('\x0b', ''))
                   for rec in records]
        self.truncate('office')
        return sum(len(r)
                   for r in self.add_records(self.app, 'office', cols, records))

    def _query(self, dml, params = []):
        with transaction(self._conn) as q:
            q.execute(dml, params)
            cols = [coldesc[0] for coldesc in q.description]
            return cols, [dict(zip(cols, row))
                          for row in q.fetchall()]

    def load_officers(self, basename="Officer.csv"):
        dml = '''select id as id_dabble
                              , name as Name
                              , email, office as office_dabble from officers'''
        cols, records = self._query(dml)
        self.truncate('officer')
        return sum(len(r)
                   for r in self.add_records(self.app, 'officer',
                                             cols, records))


def import_csv(trx, fn, table, colsize=500):
    '''Import data from a comma-separated file into a table.

    1st line contains column names; '_' is substituted for spaces.
    '''
    rows = csv.reader(open(fn))
    colnames = [n.replace(' ', '_').upper()
                for n in rows.next()]
    try:
        trx.execute('drop table %s' % table)
    except:
        pass
    trx.execute(_create_ddl(table, colnames, colsize))
    trx.executemany(_insert_dml(table, colnames),
                    [dict(zip(colnames,
                              [cell.decode('utf-8') for cell in row]))
                     for row in rows])


def _create_ddl(table, colnames, colsize):
    '''
    >>> _create_ddl('item', ('id', 'size', 'price'), 50)
    'create table "item" ("id" varchar2(50), "size" varchar2(50), "price" varchar2(50))'
    '''
    return 'create table "%s" (%s)' % (
        table, ', '.join(['"%s" varchar2(%d)' % (n, colsize)
                          for n in colnames]))


def _insert_dml(table, colnames):
    '''
    >>> _insert_dml('item', ('id', 'size', 'price'))
    'insert into "item" ("id", "size", "price") values (:id, :size, :price)'
    '''
    return 'insert into "%s" (%s) values (%s)' % (
        table,
        ', '.join(['"%s"' % n for n in colnames]),
        ', '.join([':' + n
                   for n in colnames]))


@contextmanager
def transaction(conn):
    '''Return an Oracle database cursor manager.

    :param conn: an Oracle connection
    '''
    c = conn.cursor()
    try:
        yield c
    except sqlite3.Error:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        c.close()


if __name__ == '__main__':
    import sys
    main(sys.argv)
