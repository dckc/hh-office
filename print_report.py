#!/usr/bin/env python
'''Handle web requests for printed reports from a database.

'''

from os import path, environ
import logging
import traceback
import wsgiref.handlers

# a bit of a KLUDGE...
import sys
sys.path.append(path.expanduser('~/run/lib/python2.5/site-packages/'))

import libxslt

import rlib  # http://rlib.sicompos.com/
             # 06b3e629c6f99a8b2fd1264f32db8f56  rlib-1.3.7.tar.gz

from ocap import DBOpts, dbopts
import hhtcb


PLAIN = [('Content-Type', 'text/plain')]
HTML8 = [('Content-Type', 'text/html; charset=utf-8')]
PDF = [('Content-Type', 'application/pdf')]

log = logging.getLogger(__name__)


def cgi_main():
    wsgiref.handlers.CGIHandler().run(report_if_key)


def _test_main():
    import sys

    report_name, outfn = sys.argv[1:3]

    logging.basicConfig(level=logging.DEBUG)

    def start_response(r, hdrs):
        print r
        print hdrs

    content = run_report(report_name, start_response,
                         dbopts(hhtcb.xataface_config()))
    outfp = open(outfn, 'w')
    for part in content:
        outfp.write(part)


def report_if_key(env, start_response):
    '''TCB part of the WSGI handler

    @param env: CGI environment; PATH_INFO is used to find
            a report skeleton under `templates`.

    See :func:`add_xataface_datasource` for database connection strategy.

    '''
    dbo = DBOpts(hhtcb.xataface_config())
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
               tx='reportspec.xsl',
               dsn='local_mysql'):
    '''Common TCB part of report generation

    @param report_name: used to find
           a report skeleton under `templates`,
           unless it ends in .xml, in which case
           it is used directly as the report spec.

    See :func:`add_xataface_datasource` for database connection strategy.

    '''
    from hhtcb import Dir

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


if __name__ == '__main__':
    if 'SCRIPT_NAME' in environ:
        cgi_main()
    else:
        _test_main()