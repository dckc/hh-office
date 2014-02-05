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

from subprocess import PIPE
from xml.etree import ElementTree as ET
import logging

import ocap
from hhtcb import Xataface, WSGI, MockXF


def _kludge_pkg_path():
    import sys
    from os import path as p
    sys.path.append(p.expanduser('~/run/lib/python2.5/site-packages/'))


log = logging.getLogger(__name__)


def cgi_main(mkCGIHandler, report_app):
    r'''
    >>> from wsgiref.handlers import CGIHandler
    >>> logging.basicConfig(level=logging.INFO)

    >>> report_app = MockReportApp.make()
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


def mk_report_app(report_authz, reportSpec):

    def report_app(env, start_response):
        '''
        @param env: CGI environment; PATH_INFO is used to find
                    a report skeleton under `templates`.
        '''
        try:
            report, dsn = report_authz(env)
        except IOError as e:
            start_response('403 not authorized', WSGI.PLAIN)
            return [str(e)]

        report_name = env.get('PATH_INFO', '')[1:]
        return serve_report_request(start_response, report_name,
                                    reportSpec, report, dsn)

    return report_app


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
        start_response('404 not found', WSGI.PLAIN)
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


class MockReport(object):
    def __init__(self):
        self._ds = {}

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


class MockReportApp(object):
    @classmethod
    def make(cls):
        from traceback import format_exc

        report_app = mk_caps('/here', MockXF, MockXF.open_rd,
                             mkRlib=lambda: MockReport(),
                             Popen=MockOS.popen)

        return WSGI.error_middleware(format_exc, report_app)


class MockOS(object):
    @classmethod
    def popen(cls, args, stdout=None):
        return cls()

    def communicate(self, input=None):
        return 'communicate stuff', ''


def mkReportMaker(mkRlib, xf,
                  dsn='local_mysql'):
    def reportMaker():
        opts = xf.dbopts()
        log.debug('db opts: %s', opts)
        report = mkRlib()
        report.add_datasource_mysql(dsn, *opts)

        return report, dsn

    return reportMaker


def mk_caps(cwd, os_path, open_rd, mkRlib, Popen):
    here = ocap.Rd(cwd, os_path, open_rd)
    xf = Xataface.make(here)
    reportMaker = mkReportMaker(mkRlib=mkRlib, xf=xf)
    reportSpec = mkReportSpec(Popen, here)

    return mk_report_app(
        report_authz=xf.mk_qs_facet(reportMaker),
        reportSpec=reportSpec)


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

        report_app = mk_caps(cwd=path.dirname(__file__),
                             os_path=path,
                             open_rd=lambda n: open(n),
                             mkRlib=mkRlib,
                             Popen=Popen)

        if 'SCRIPT_NAME' in environ:
            report_appE = WSGI.error_middleware(format_exc, report_app)

            cgi_main(mkCGIHandler=lambda: CGIHandler(),
                     report_app=report_appE)
        else:
            from sys import argv, stdout

            logging.basicConfig(level=logging.DEBUG)

            def argv_wr(n):
                if n not in argv:
                    raise IOError()
                return open(n, 'w')

            _test_main(argv[:], stdout, argv_wr, report_app)

    _with_caps()
