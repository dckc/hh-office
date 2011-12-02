'''claim_sync -- sync claims between hh-office and FreeClaims

TODO: get batches of claims from hh-office
'''
import time
import logging
from collections import namedtuple

from mechanize._beautifulsoup import BeautifulSoup as HTML
import mechanize

log = logging.getLogger(__name__)


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

    def upload_file(self, claim_fn, pg='upload.asp', form='Upload'):
        log.debug('upload: open(%s).', pg)
        r3 = self.open(pg)
        scrub_nested_form(self, r3)
        log.debug('upload: select_form(%s).', form)
        self.select_form(form)

        log.debug('upload: add_file(%s).', claim_fn)
        self.form.add_file(open(claim_fn), 'text/plain', claim_fn)
        log.debug('upload: submit claims.')
        r4 = self.submit()
        # @@TODO: parse server-assigned name
        return r4.get_data()

    def upload_batch(self, claim_fn):
        '''Upload a file of claims and wait for the new batch number.

        @return: list of batches for this account, starting with the new one.

        We assume noone else is uploading concurrently.
        '''
        before = self.batches()
        self.upload_file(claim_fn)
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


def _test_main(argv):
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
        else:
            raise ValueError('huh? ' + action)


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
    _test_main(sys.argv)
