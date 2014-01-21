#!/usr/bin/env python
'''Handle web requests for printed reports from a database.

uses xsltproc

TODO: move xsltproc processing to design time with make

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
from subprocess import PIPE
from xml.etree import ElementTree as ET
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


def cgi_main(mkCGIHandler, report_app):
    r'''
    >>> from wsgiref.handlers import CGIHandler
    >>> logging.basicConfig(level=logging.INFO)

    >>> report_app = Mock.report_app()
    >>> from os import environ
    >>> environ['QUERY_STRING'] = 'key=sekret'
    >>> environ['PATH_INFO'] = '/weekly_groups'

    >>> cgi_main(lambda: CGIHandler(), report_app)
    ... # normalize CRLF vs LF
    ... # doctest: +NORMALIZE_WHITESPACE
    Status: 200 ok
    Content-type: application/pdf
    Content-Length: 15
    <BLANKLINE>
    pdf stuff here

    '''
    mkCGIHandler().run(report_app)


def _test_main(argv, stdout, argv_wr, report_app):
    report_name, outfn = argv[1:3]

    def start_response(r, hdrs):
        print >>stdout, r
        print >>stdout, hdrs

    content = report_app(dict(PATH_INFO='/' + report_name), start_response)

    outfp = argv_wr(outfn)
    for part in content:
        outfp.write(part)


def mk_report_app(format_exc, report_authz, reportSpec):

    def report_app(env, start_response):
        '''
        @param env: CGI environment; PATH_INFO is used to find
                    a report skeleton under `templates`.
        '''
        try:
            report, dsn = report_authz(env)
        except IOError as e:
            start_response('403 not authorized', PLAIN)
            return [str(e)]

        report_name = env.get('PATH_INFO', '')[1:]
        try:
            return serve_report_request(start_response, report_name,
                                        reportSpec, report, dsn)
        except:  # pylint: disable-msg=W0703,W0702
            start_response('500 internal error', PLAIN)
            return [format_exc()]

    return report_app


def report_if_key(configRd, reportMaker):
    r'''
    >>> here = ocap.Rd('/here', Mock, Mock.open_rd)
    >>> configRd = xataface_config(here)
    >>> reportMaker = mkReportMaker(lambda: Mock(), configRd)
    >>> ck = report_if_key(configRd, reportMaker)

    >>> report, dsn = ck({'QUERY_STRING': 'key=sekret'})
    >>> report._ds['local_mysql']
    ('localhost', 'mickey_mouse', 'club', 'all_my_friends')

    >>> ck({'QUERY_STRING': ''})
    Traceback (most recent call last):
      ...
    KeyError: 'missing key parameter'

    >>> ck({'QUERY_STRING': 'key=secret'})
    Traceback (most recent call last):
      ...
    IOError: report key does not match.
    '''
    def check_config(env):
        '''
        @param env: CGI environment; PATH_INFO is used to find
                    a report skeleton under `templates`.
        '''
        k = parse_qs(env.get('QUERY_STRING', '')).get('key')
        if not k:
            raise KeyError('missing key parameter')

        config = patched_config(configRd)

        if config.get(DB_SECTION, 'report_key') not in k:
            raise IOError('report key does not match.')

        return reportMaker()

    return check_config


def mkReportSpec(Popen, here,
                 tx='reportspec.xsl',
                 xsltproc='xsltproc'):
    templates = here.subRd('templates')
    txpath = here.subRd(tx)
    log.debug('templates: %s txpath: %s', templates, txpath)

    def xslt(tx, doc):
        p = Popen([xsltproc, '--novalid', str(tx), str(doc)],
                  stdout=PIPE)
        out, err = p.communicate()
        return out

    def reportSpec(report_name):
        tx, template, fmt = (
            (None, templates.subRd(report_name), 'TXT')
            if report_name.endswith('.xml') else
            (txpath, templates.subRd(report_name + '.html'), 'PDF'))

        log.debug('template exists? %s', template)
        if not template.exists():
            return None, None, None

        qdoc = ET.XML(template.fp().read())
        q = qdoc.find('.//*[@class="query"]').text

        spec_text = (xslt(tx, template) if tx
                     else template.fp().read())

        return spec_text, fmt, q

    return reportSpec


def serve_report_request(start_response, report_name,
                         reportSpec, report, dsn):
    '''Serve the request, now that we have a report with datasource.

    The caller is responsible to make 5xx responses out of any
    exceptions raised.

    @param start_response: as per WSGI; called with 200 OK.
    @param report: an intilized rlib__ report with datasource.
    @param dsn: data source name to associate with query.

    @return: an iterator as per WSGI; contains a PDF document.

    __ http://newrlib.sicom.com/~rlib/index.php/Documentation_XML
    __ http://rlib.sicompos.com/

    .. todo: cite WSGI
    '''
    spec_txt, outfmt, report_dml = reportSpec(report_name)
    if not spec_txt:
        start_response('404 not found', PLAIN)
        return ['no such report spec\n']

    log.debug('report dml: %s', report_dml)
    report.add_query_as(dsn, report_dml, 'arbitrary_report_name')

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
    import pkg_resources as pkg

    content = {'/here/conf.ini':
               '\n'.join([line.strip()
                          for line in '''
               [_database]
               report_key=sekret
               host="localhost"
               user="mickey_mouse"
               password="club"
               name="all_my_friends"
                          '''.split('\n')]),
               '/here/templates/weekly_groups.html':
               pkg.resource_string(__name__, 'templates/weekly_groups.html')}

    def __init__(self):
        self._ds = {}

    @classmethod
    def report_app(cls):
        from traceback import format_exc

        here = ocap.Rd('/here', Mock, Mock.open_rd)

        configRd = xataface_config(here)
        reportMaker = mkReportMaker(mkRlib=lambda: cls(),
                                    configRd=configRd)
        reportSpec = mkReportSpec(cls.popen, here)

        return mk_report_app(
            format_exc,
            report_authz=report_if_key(configRd, reportMaker),
            reportSpec=reportSpec)

    @classmethod
    def popen(cls, args, stdout=None):
        return cls()

    def communicate(self, input=None):
        return 'communicate stuff', ''

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

    @classmethod
    def exists(cls, path):
        return path in cls.content

    def add_datasource_mysql(self, dsn, host, username, password, name):
        self._ds[dsn] = (host, username, password, name)

    def add_query_as(self, dsn, q, report_name):
        pass

    def add_report_from_buffer(self, txt):
        pass

    def set_output_format_from_text(self, fmt):
        pass

    def execute(self):
        pass

    def get_content_type_as_text(self):
        return 'Content-type: application/pdf\n'

    def get_output(self):
        return 'pdf stuff here\n'


def mkReportMaker(mkRlib, configRd,
                  dsn='local_mysql'):
    def reportMaker():
        config = patched_config(configRd)
        opts = [config.get(DB_SECTION, k)[1:-1]
                for k in ['host', 'user', 'password', 'name']]
        log.debug('db opts: %s', opts)
        report = mkRlib()
        report.add_datasource_mysql(dsn, *opts)

        return report, dsn

    return reportMaker


def xataface_config(here,
                    ini='conf.ini'):
    return here.subRd(ini)


DB_SECTION = '_database'


def patched_config(configRd):
    config = SafeConfigParser()
    config.readfp(Prefix(configRd.fp(), '[DEFAULT]'), str(configRd))
    return config


if __name__ == '__main__':
    def _with_caps():
        #import traceback
        from wsgiref.handlers import CGIHandler

        from os import environ, path
        from subprocess import Popen
        from traceback import format_exc

        def mkRlib():
            from rlib import Rlib
            return Rlib()

        here = ocap.Rd(path.dirname(__file__), path,
                       lambda n: open(n))
        configRd = xataface_config(here)
        reportMaker = mkReportMaker(mkRlib=mkRlib,
                                    configRd=configRd)
        reportSpec = mkReportSpec(Popen, here)

        if 'SCRIPT_NAME' in environ:
            report_app = mk_report_app(
                format_exc,
                report_authz=report_if_key(configRd, reportMaker),
                reportSpec=reportSpec)

            cgi_main(mkCGIHandler=lambda: CGIHandler(),
                     report_app=report_app)
        else:
            from sys import argv, stdout

            logging.basicConfig(level=logging.DEBUG)

            def argv_wr(n):
                if n not in argv:
                    raise IOError()
                return open(n, 'w')

            report_app = mk_report_app(
                format_exc,
                report_authz=lambda config: reportMaker(),
                reportSpec=reportSpec)

            _test_main(argv[:], stdout, argv_wr, report_app)

    _with_caps()
