import mechanize
import time
import logging


log = logging.getLogger(__name__)


def _test_main(argv,
    members_login_pg='https://sfreeclaims.anvicare.com/docs/member_login.asp'):
    username, password, claim_fn = argv[1:4]

    logging.basicConfig(level=logging.DEBUG)
    
    ua = mechanize.Browser()

    log.debug('1. open(%s)', members_login_pg)
    ua.open(members_login_pg)
    ua.select_form(name="loginForm")
    ua['username'] = username
    ua['userpassword'] = password
    log.debug('2. submit creds.')
    ua.submit()

    log.debug('2. open(%s) to get previous latest batch number.',
              'ViewBatch.asp')
    rprev = ua.open('ViewBatch.asp')
    print '----------------ViewBatch.asp initial', '\n', rprev.get_data()

    log.debug('3. open(upload.asp).')
    r3 = ua.open('upload.asp')
    print '----------------upload.asp', '\n', r3.get_data()
    scrub_nested_form(ua, r3)

    log.debug('3.a select_form(%s).', 'Upload')
    ua.select_form('Upload')

    log.debug('3.b add_file(%s).', claim_fn)
    ua.form.add_file(open(claim_fn), 'text/plain', claim_fn)
    log.debug('4. submit claims.')
    r4 = ua.submit()
    print '----------------submit response', '\n', r4.get_data()

    while 1:
        time.sleep(1)
        log.debug('5.. open(%s)', 'ViewBatch.asp')
        rbatches = ua.open('ViewBatch.asp')
        content = rbatches.get_data()
        print '----------------ViewBatch.asp', '\n', content
        break  #@@


def scrub_nested_form(ua, response):
    # http://stackoverflow.com/questions/1782368/is-it-possible-to-hook-up-a-more-robust-html-parser-to-python-mechanize/5039584#5039584
    # http://stackoverflow.com/questions/7135964/submitting-nested-form-with-python-mechanize
    tweak = '''<form method="POST" action="FRCLsaveClaim" enctype="multipart/form-data" name="uploadClaimForm">'''
    log.debug('tweak code')
    txt = response.get_data()
    if tweak in txt:
        log.debug('tweaking!')
        response.set_data(txt.replace(tweak, '').replace(
            '</form> </center>', '</center>'))
        ua.set_response(response)


def _test_parse(argv):
    x, y, doc_fn = argv[1:4]
    import ClientForm
    forms = ClientForm.ParseFile(open(doc_fn), 'http://example/')
    print forms


if __name__ == '__main__':
    import sys
    #_test_parse(sys.argv)
    _test_main(sys.argv)
