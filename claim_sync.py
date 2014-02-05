'''claim_sync -- sync claims between hh-office and FreeClaims

TODO:
  1. 'make claims' redirects to this python app with a list of visit ids
  2. Response is a confirmation page that
     a. enumerates the visits (perhaps date, client name, dx, cpt, price)
     b. includes the CSV data in a textarea
     c. offers to Submit the CSV data to freeclaims
  3. Response has either
     a. a link to the new batch on FreeClaims and a link back to Xata,
        with the claim_uid and bill_date of the relevant Visits updated, or
     b. a "try again shortly" link (perhaps it tries again automatically)
'''
import time
import logging
from collections import namedtuple
import datetime
from xml.sax import saxutils
import StringIO
import csv

from mechanize._beautifulsoup import BeautifulSoup as HTML
import mechanize
import MySQLdb
import paste

import hhtcb
from ocap import DBOpts
from export_claims import format_claims

log = logging.getLogger(__name__)


def app_factory(config):
    logging.basicConfig(level=logging.INFO)
    dbo = DBOpts(hhtcb.xataface_config())
    return SyncApp(dbo)


def test_main(argv):
    import sys
    import pprint

    logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
    ua = FreeClaimsUA()

    while argv[1:]:
        action = argv[1]
        if action == '--login':
            username, password = argv[2:4]
            del argv[1:4]
            ua.login(username, password)
        elif action == '--upload':
            claim_fn = argv[2]
            del argv[1:3]
            ua.upload(claim_fn)
        elif action == '--batches':
            del argv[1]
            pprint.pprint(ua.batches())
        elif action == '--batches-local':
            doc_fn = argv[2]
            del argv[1:3]
            pprint.pprint(ua._batches(open(doc_fn).read()))
        elif action == '--claims':
            del argv[1]
            batches_flatten(sys.stdout,
                            [(batch, ua.claims(batch))
                             for batch in ua.batches()])
        else:
            raise ValueError('huh? ' + action)


class SyncApp(object):
    PLAIN = [('Content-Type', 'text/plain')]
    HTML8 = [('Content-Type', 'text/html; charset=utf-8')]

    def __init__(self, dbo,
                 title='Hope Harbor FreeClaims Helper'):
        self._dbo = dbo
        self._title = title

    def __call__(self, env, start_response):
        '''Check authorization, login to the DB, and dispatch to show/upload.
        '''
        try:
            host, user, password, name = self._dbo.webapp_login(env)
        except KeyError:
            start_response('400 bad request', self.PLAIN)
            return ['missing key parameter ']
        except OSError:
            start_response('401 unauthorized', self.PLAIN)
            return ['report key does not match.']

        # scrub user input
        params = paste.request.parse_formvars(env)
        visit_ids = [int(visit_id)
                     for visit_id in params.get('visits').split(',')]
        log.debug('visit_ids: %s', visit_ids)

        conn = MySQLdb.connect(host=host, user=user, passwd=password, db=name)
        content, claims = format_claims(conn, visit_ids)

        if env['REQUEST_METHOD'] == 'POST':
            u, p = params.get('user'), params.get('password')
            batches, results = self.upload(u, p, content, claims)
            update_visits(conn, claims, results)
            start_response('200 ok', self.HTML8)
            return format_upload_results(self._title, batches[0], results)
        else:
            start_response('200 ok', self.HTML8)
            base = env['SCRIPT_NAME'] + env['PATH_INFO']
            key = params.get('key')
            return self.show(base, key, visit_ids, content, claims)

    def show(self, base, key, visit_ids, content, claims,
             default_user='4482'):
        return doc_with(
            self._title,
            ['<h1>Insurance Claim Batch</h1>\n',
             '<form method="POST" action="?key=%s&visits=%s">\n' % (
                 key, ','.join(map(str, visit_ids))),
             '<ol>\n'] +
            [piece for claim in claims
             for piece in
             (['  <li>%s<br />%s $%s<br />DX: %s %s <ol>\n' % (
                 saxutils.escape(claim['detail'][
                     'Insurance Company Name']),
                 saxutils.escape(claim['detail']['2-PatientName']),
                 claim['detail']['28-TotalCharge'],
                 claim['detail']['21.1-Diagnosis'],
                 claim['detail']['21.2-Diagnosis'] or '')] +
              ['    <li>on %s CPT: %s $%s</li>\n' % (
                  item['24.1.a-DOSFrom'],
                  item['24.1.d-CPT'],
                  item['24.1.f-Charges'])
               for item in claim['items']] +
              ['</ol>\n', '</li>\n'])] +
            ['</ol>\n',
             '<p><em>Submitting this form will upload a "file"',
             '  to FreeClaims and wait for acknowledgement.',
             ' It may take a few minutes.</em></p>',
             '<label>FreeClaims file data:'
             '<textarea name="claim_data">\n'] +
            [saxutils.escape(piece) for piece in content] +
            ['</textarea></label>\n',
             '<p>FreeClaims user id: ',
             '<input name="user" value="%s"/></p>' % default_user,
             '<p>FreeClaims password: ',
             '<input name="password" type="password" /></p>',
             '<input type="submit" value="Upload" /></p>',
             '</form>\n'])

    def upload(self, u, p, content, claims, fn='claim_sync.csv'):
        ua = FreeClaimsUA()
        ua.login(u, p)
        txt = ''.join(content)
        data = StringIO.StringIO(txt)
        log.info('uploading %d bytes', len(txt))
        batches = ua.upload_batch_data(data, fn)
        log.info('found batch: %s; getting claims', batches[0].batch_no)
        results = ua.claims(batches[0])
        log.info('found %d claims', len(results))
        return batches, results


def update_visits(conn, claims, results):
    for cin, cout in zip(claims, results):
        visit_ids = cin['visit_ids']
        sql = ("""update Visit v
               set claim_uid = concat(%%s, ',', %%s)
               where v.id in (%s)""" % ', '.join(map(str, visit_ids)))
        log.info('Updating (%s) to trace %s, batch %s\nSQL:%s',
                 visit_ids, cout.trace_no, cout.batch, sql)
        work = conn.cursor()
        work.execute(sql, (cout.trace_no, cout.batch))
        conn.commit()


def doc_with(title, body):
    return (['<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml">\n',
             '<head><title>%s</title></head>\n' % title,
             '<body>\n'] + body +
            ['</body>\n',
             '</html>\n'])


def format_upload_results(title, batch, results):
    return doc_with(
        title,
        ['<table border="1">\n',
         '<tr>\n',
         '<th>Trace</th><th>Batch</th><th>Status</th>',
         '<th>Last</th><th>First</th><th>Acct</th>',
         '<th>Service Date</th><th>Date Received</th>',
         '</tr>\n'] +
        [piece for cout in results for piece in
         ['<tr>',
          '<td><a href="%s%s">%s</a></td>' % (
              FreeClaimsUA.base, cout.href, cout.trace_no),
          '<td><a href="%s%s">%s</a></td>' % (
              FreeClaimsUA.base, batch.href, batch.batch_no),
          '<td>%s</td>' % cout.status,
          '<td>%s</td>' % cout.last,
          '<td>%s</td>' % cout.first,
          '<td>%s</td>' % cout.acc_no,
          '<td>%s</td>' % cout.service_date,
          '<td>%s</td>' % cout.date_received,
          '</tr>'
          ]] +
        ['</table>',
         '<p><strong>To update billing dates, return to Hope Harbor',
         ' Attendance using the back button'
         ' and choose the Update action button.',
         '</strong></p>'])


class FreeClaimsUA(mechanize.Browser):
    base = 'https://sfreeclaims.anvicare.com/docs/'

    def login(self, username, password, pg='member_login.asp'):
        log.debug('login: open(%s)', self.base + pg)
        self.open(self.base + pg)
        self.select_form(name="loginForm")
        self['username'] = username
        self['userpassword'] = password
        log.debug('login: submit creds.')
        self.submit()

    def batches(self, pg='ViewBatch.asp'):
        log.debug('batches: open(%s).', pg)
        return self._batches(self.open(pg).get_data())

    def _batches(self, txt):
        doc = HTML(txt)
        doc.done()
        t = doc.html.first('table', {'align': 'Center'})
        return [batch(row('td')[1])
                # skip heading row
                for row in t('tr')[1:]]

    def claims(self, batch):
        log.debug('claims: open (%s)', batch.href)
        doc = HTML(self.open(batch.href).get_data())
        doc.done()
        t = doc.html.first('table', {'align': 'Center'})
        return [claim(row) for row in t('tr')[1:]]

    def upload_file(self, claim_fn):
        self.upload_data(open(claim_fn), claim_fn)

    def upload_data(self, claim_fp, claim_fn, pg='upload.asp', form='Upload'):
        log.debug('upload: open(%s).', pg)
        r3 = self.open(pg)
        scrub_nested_form(self, r3)
        log.debug('upload: select_form(%s).', form)
        self.select_form(form)

        log.debug('upload: add_file(%s).', claim_fn)
        self.form.add_file(claim_fp, 'text/plain', claim_fn)
        log.debug('upload: submit claims.')
        r4 = self.submit()
        # @@TODO: parse server-assigned name
        return r4.get_data()

    def upload_batch(self, claim_fn):
        self.upload_batch_data(open(claim_fn), claim_fn)

    def upload_batch_data(self, claim_fp, claim_fn):
        '''Upload a file of claims and wait for the new batch number.

        @return: list of batches for this account, starting with the new one.

        We assume noone else is uploading concurrently.
        '''
        before = self.batches()
        self.upload_data(claim_fp, claim_fn)
        while 1:
            log.debug('wait: sleep 2')
            time.sleep(2)
            b = self.batches()
            if b[0].batch_no > before[0].batch_no:
                return b


Batch = namedtuple('Batch', 'batch_no href')


def batch(cell):
    '''
    >>> batch(HTML('<td nowrap="nowrap">&nbsp;'
    ...              '<a href="ViewClaims.asp?batch_no=2027161">2027161</a>'
    ...             '</td>'))
    Batch(batch_no=2027161, href='ViewClaims.asp?batch_no=2027161')
    '''
    return Batch(int(cell.a.contents[0]), cell.a['href'])


Claim = namedtuple('Claim',
                   'trace_no href batch status '
                   'last first acc_no service_date date_received')


def batches_flatten(out, batches_claims):
    co = csv.writer(out)
    co.writerow('''batch_no trace_no status
                   last first acc_no client_id
                   service_date date_received'''.split())

    co.writerows([
        (batch.batch_no,
         claim.trace_no, claim.status,
         claim.last, claim.first,
         claim.acc_no, claim.acc_no.split('.')[-1],
         claim.service_date, claim.date_received)
        for batch, claims in batches_claims
        for claim in claims])


def claim(row):
    '''
    >>> claim(HTML(_CLAIM_MARKUP))
    ... # doctest: +NORMALIZE_WHITESPACE
    Claim(trace_no=33298999, href='viewonehcfa.asp?trace_no=33298999',
          batch=2027161, status='ACCEPTED', last='SMITH', first='STEVEN',
          acc_no='JAM.STE.10999',
          service_date=datetime.datetime(2011, 11, 10, 0, 0),
          date_received=datetime.datetime(2011, 12, 2, 0, 0))
    '''
    txts = [cell.contents[0].replace('&nbsp;', '') for cell in row('td')]
    trace_cell = row('td')[1]
    return Claim(int(trace_cell.a.contents[0]), trace_cell.a['href'],
                 int(txts[2]), txts[3], txts[4], txts[5], txts[6],
                 datetime.datetime.strptime(txts[9], '%m/%d/%Y'),
                 datetime.datetime.strptime(txts[15], '%m/%d/%Y'))

_CLAIM_MARKUP = '''
                            <tr bgcolor=ddf7f7 >
                                <td class="g" align="right">1</td>


                <td class="g"><a href='viewonehcfa.asp?trace_no=33298999'
                target='_new'>33298999</a></td>


                                <td class="g">2027161</td>
                                <td class="g">ACCEPTED</td>
                                <td class="g">&nbsp;SMITH</td>
                                <td class="g">&nbsp;STEVEN</td>
                                <td class="g">&nbsp;JAM.STE.10999</td>
                                <td class="g">&nbsp;60999</td>
                                <td class="g">&nbsp;MDONL</td>
                                <td class="g">&nbsp;11/10/2011</td>
                                <td class="g" align="right">&nbsp;120.00</td>
                                <td class="g">&nbsp;</td>
                                <td class="g">&nbsp;</td>
                                <td class="g">&nbsp;JOHNSON</td>
                                <td class="g">&nbsp;WILLIAM</td>
                         <td class="g" align="right">&nbsp;12/2/2011</td>
                            </tr>
'''


def scrub_nested_form(ua, response):
    # Is it possible to hook up a more robust HTML parser to Python mechanize?
    # http://stackoverflow.com/questions/1782368/
    #  submitting-nested-form-with-python-mechanize
    # http://stackoverflow.com/questions/7135964/
    tweak = ('''<form method="POST" action="FRCLsaveClaim" '''
             '''enctype="multipart/form-data" name="uploadClaimForm">''')
    log.debug('tweak code')
    txt = response.get_data()
    if tweak in txt:
        log.debug('tweaking!')
        response.set_data(txt.replace(tweak, '').replace(
            '</form> </center>', '</center>'))
        ua.set_response(response)


if __name__ == '__main__':
    import sys
    test_main(sys.argv)
