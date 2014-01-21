#!/usr/bin/env python
'''Handle web requests for printed reports from a database.

  # http://rlib.sicompos.com/
             # 06b3e629c6f99a8b2fd1264f32db8f56  rlib-1.3.7.tar.gz
#Subject: compiling with python
#For some reason configure does not pick up python unless you supply a prefix.
#
#/configure --with-pythonver=2.5 --prefix=/usr
#http://osdir.com/ml/text.rlib.user/2008-07/msg00002.html
'''

from ConfigParser import SafeConfigParser
from cgi import parse_qs
import logging

import ocap


def _kludge_pkg_path():
    import sys
    from os import path as p
    sys.path.append(p.expanduser('~/run/lib/python2.5/site-packages/'))


PLAIN = [('Content-Type', 'text/plain')]
HTML8 = [('Content-Type', 'text/html; charset=utf-8')]
PDF = [('Content-Type', 'application/pdf')]

log = logging.getLogger(__name__)


def cgi_main(mkCGIHandler):
    mkCGIHandler().run(report_if_key)


def _test_main(argv, stdout):
    report_name, outfn = argv[1:3]

    def start_response(r, hdrs):
        print >>stdout, r
        print >>stdout, hdrs

    content = run_report(report_name, start_response,
                         dbopts(xataface_config()))  #@@
    outfp = open(outfn, 'w')
    for part in content:
        outfp.write(part)


def report_if_key(env, start_response):
    '''TCB part of the WSGI handler

    @param env: CGI environment; PATH_INFO is used to find
            a report skeleton under `templates`.

    See :func:`add_xataface_datasource` for database connection strategy.

    '''
    dbo = DBOpts(xataface_config())  #@@
    try:
        opts = dbo.webapp_login(env)
    except KeyError:
        start_response('400 bad request', PLAIN)
        return ['missing key parameter ']
    except OSError:
        start_response('401 unauthorized', PLAIN)
        return ['report key does not match.']

    return run_report(env.get('PATH_INFO', '')[1:], start_response, opts)


def run_report(report_name, start_response, opts,
               tx='reportspec.xsl'):
    '''Common TCB part of report generation

    @param report_name: used to find
           a report skeleton under `templates`,
           unless it ends in .xml, in which case
           it is used directly as the report spec.

    See :func:`add_xataface_datasource` for database connection strategy.

    '''
    #@@from hhtcb import Dir

    here = Dir(path.dirname(__file__))
    templates = here.subdir('templates')
    txpath = here.file(tx)

    report = rlib.Rlib()
    log.debug('db opts: %s', opts)
    report.add_datasource_mysql(dsn, *opts)

    try:
        return serve_report_request(start_response, templates, report_name,
                                    txpath, report, dsn)
    except:  # pylint: disable-msg=W0703,W0702
        start_response('500 internal error', PLAIN)
        return [traceback.format_exc()]


def serve_report_request(start_response, templates, report_name,
                         txpath, report, dsn):
    '''Less trusted part of the WSGI handler.

    The caller is responsible to make 5xx responses out of any
    exceptions raised.

    @param start_response: as per WSGI; called with 200 OK.
    @param templates: a directory of report skeletons or specs;
                     The skeleton/spec also specifies
                     the mysql query to run in an element with
                     @class="query".
    @param txpath: File of an XSLT transformation that produces
                  `rlib report definitions`__ from HTML skeletons.
    @param report: an intilized rlib__ report with datasource.
    @param dsn: data source name to associate with query.

    @return: an iterator as per WSGI; contains a PDF document.

    __ http://newrlib.sicom.com/~rlib/index.php/Documentation_XML
    __ http://rlib.sicompos.com/

    .. todo: cite WSGI
    '''

    if report_name.endswith('.xml'):
        tx = None
        template = templates.file(report_name)
    else:
        tx = libxslt.parseStylesheetDoc(txpath.xml_content())
        template = templates.file(report_name + '.html')

    if not template.exists():
        start_response('404 not found', PLAIN)
        return ['no such report spec\n']

    if tx:
        skel = template.xml_content()
        ctxt = skel.xpathNewContext()
        spec = tx.applyStylesheet(skel, None)
        outfmt = 'PDF'
    else:
        spec = template.xml_content()
        ctxt = spec.xpathNewContext()
        outfmt = 'TXT'

    report_dml = ctxt.xpathEval('//*[@class="query"]')[0].content
    log.debug('report dml: %s', report_dml)
    report.add_query_as(dsn, report_dml, 'arbitrary_report_name')

    spec_txt = spec.serialize()
    report.add_report_from_buffer(spec_txt)

    # todo: try different font:
    # report.set_output_parameter("pdf_fontname", 'helvetica')

    # I'm trying to get rid of:
    # encoding is NULL or invalid [C]... using en_US
    # but this doesn't seem to change anything.
    # myreport.set_output_encoding('UTF-8')
    report.set_output_format_from_text(outfmt)
    report.execute()

    log.debug('raw headers: %s', report.get_content_type_as_text())
    hd_txt = report.get_content_type_as_text()
    hdrs = [tuple(line.strip().split(': ', 1))
            for line in hd_txt.split('\n')[:-1]]  # skip head/body separator
    log.debug('parsed headers: %s', hdrs)
    start_response('200 ok', hdrs)
    return [report.get_output()]


class Prefix(object):
    '''work-around: xataface needs options before the 1st [section]
    '''
    def __init__(self, fp, line):
        self._fp = fp
        self._l = line

    def readline(self):
        if self._l:
            l = self._l
            self._l = None
            return l
        else:
            return self._fp.readline()


class Mock(object):
    def __init__(self):
        self._ds = {}

    content = {'/here/conf.ini':
               '\n'.join([line.strip()
                          for line in '''
               [_database]
               report_key=sekret
               host="localhost"
               user="mickey_mouse"
               password="club"
               name="all_my_friends"
                          '''.split('\n')])}

    @classmethod
    def open_rd(cls, n):
        from StringIO import StringIO
        return StringIO(cls.content[n])

    @classmethod
    def abspath(cls, p):
        import posixpath
        return posixpath.abspath(p)

    @classmethod
    def join(cls, *paths):
        import posixpath
        return posixpath.join(*paths)

    def add_datasource_mysql(self, dsn, host, username, password, name):
        self._ds[dsn] = (host, username, password, name)


def mkReportMaker(mkRlib, configRd,
                  DB_SECTION='_database',
                  dsn='local_mysql'):
    r'''
    >>> here = ocap.Rd('/here', Mock, Mock.open_rd)
    >>> configRd = xataface_config(here)
    >>> rm = mkReportMaker(lambda: Mock(), configRd)

    >>> report = rm({'QUERY_STRING': 'key=sekret'})
    >>> report._ds['local_mysql']
    ('localhost', 'mickey_mouse', 'club', 'all_my_friends')

    >>> rm({'QUERY_STRING': ''})
    Traceback (most recent call last):
      ...
    KeyError: 'missing key parameter'

    >>> rm({'QUERY_STRING': 'key=secret'})
    Traceback (most recent call last):
      ...
    IOError: report key does not match.
    '''

    def reportMaker(env):
        k = parse_qs(env.get('QUERY_STRING', '')).get('key')
        if not k:
            raise KeyError('missing key parameter')

        config = patched_config(configRd)
        if config.get(DB_SECTION, 'report_key') not in k:
            raise IOError('report key does not match.')

        opts = [config.get(DB_SECTION, k)[1:-1]
                for k in ['host', 'user', 'password', 'name']]
        log.debug('db opts: %s', opts)
        report = mkRlib()
        report.add_datasource_mysql(dsn, *opts)

        return report

    return reportMaker


def xataface_config(here,
                    ini='conf.ini'):
    return here.subRd(ini)


def patched_config(configRd):
    config = SafeConfigParser()
    config.readfp(Prefix(configRd.fp(), '[DEFAULT]'), str(configRd))
    return config


if __name__ == '__main__':
    def _with_caps():
        #import traceback
        from wsgiref.handlers import CGIHandler

        from os import environ

        #@@import rlib
        #@@import libxslt
        #@@here = path.dirname(__file__)

        if 'SCRIPT_NAME' in environ:
            cgi_main(mkCGIHandler=lambda: CGIHandler())
        else:
            from sys import argv, stdout

            logging.basicConfig(level=logging.DEBUG)
            _test_main(argv[:], stdout)
