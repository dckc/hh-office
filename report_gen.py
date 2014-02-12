'''Generate office report from design document and SQL data.

refs:
 - `PyFPDF 1.6 Reference Manual`__
 - `Tutorial`__

__ https://code.google.com/p/pyfpdf/wiki/ReferenceManual
__ https://code.google.com/p/pyfpdf/wiki/Tutorial

'''

from collections import namedtuple
from contextlib import contextmanager
from datetime import datetime
from xml.etree import ElementTree as ET
import logging

from fpdf import FPDF

import ocap
from hhtcb import Xataface

log = logging.getLogger(__name__)


def main(argv, stdout, cal, connect, templates):
    '''
    Note `_with_caps()` below for `least-authority style`__.

    __ http://www.madmode.com/2013/python-capability-idioms-part-1.html
    '''
    report_name = argv[1]
    rpt = OfficeReport.make(templates / (report_name + '.html'), cal)
    rpt.run(connect)
    stdout.write(rpt.pdf_string())
    raise NotImplementedError(rpt.todos)


ColFmt = namedtuple('Column', ['th', 'field',
                               'literal', 'filler', 'blank', 'align'])
Break = namedtuple('Break', ['name', 'key_cols', 'colfmts', 'footfmts'])


class OfficeReport(FPDF):
    portrait, landscape = 'P', 'L'
    font = 'Courier'
    plain, bold = '', 'B'
    full_line = 0
    then_right, then_newline, then_below = 0, 1, 2
    align_left, align_center, align_right = 'L', 'C', 'R'
    normal_line_height = 1.2
    black, grey, light_grey, white = 0, 0xd0, 0xe5, 0xff

    def __init__(self, design, fns,
                 unit='pt', format='Letter',
                 detail_size=10):
        FPDF.__init__(self, unit=unit, format=format)
        self.todos = set()
        self.design = design
        self._fns = fns
        self._first_line = True

    @classmethod
    def make(cls, rd, cal):
        return cls(ET.parse(rd.fp()), field_functions(cal))

    def run(self, connect):
        self._parse_design()
        self._start_page()
        self._detail(self._data(connect))

    def _parse_design(self,
                      default_size=10,
                      sizes=[('small-print', 8),
                             ('medium-print', 9)]):
        body = HTML.by_class(self.design, 'body', 'rlib')[0]
        self._orientation = (
            self.landscape
            if HTML.has_class(body, 'landscape')
            else self.portrait)
        self.right_margin = (10 if self._orientation == self.landscape
                             else 7.5) * 72
        self._report_header = HTML.by_class(body, 'h1', 'ReportHeader')[0].text

        pghd = HTML.by_class(body, 'h2', 'PageHeader')[0]
        self._pg_colfmts = self._parse_colfmts(pghd, pghd)

        explicit_sizes = [sz for (n, sz) in sizes
                          if HTML.has_class(body, n)]
        self.detail_size = (explicit_sizes[-1] if explicit_sizes
                            else default_size)
        detail = HTML.by_class(body, "table", 'Detail')[0]
        self._detail_colfmts = self._parse_colfmts(
            HTML.the(detail, "h:thead/h:tr[1]"),
            HTML.the(detail, "h:tbody/h:tr[1]"),
            all_fields=True)

        self._breaks = [
            Break(name=breakrow.attrib['id'],
                  key_cols=sorted(set([th.attrib['id']
                                       for th in breakrow
                                       if 'id' in th.attrib])),
                  footfmts=self._footfmts(breakrow.attrib['id'], detail),
                  colfmts=self._parse_colfmts(breakrow, breakrow))
            for breaks_table in HTML.by_class(body, 'table', "Breaks")[:1]
            for breakrow in HTML.the(breaks_table, 'h:thead')]

        log.debug('break footer colfmt fillers: %s',
                  [c.filler
                   for b in self._breaks if b.footfmts
                   for c in b.footfmts])
        log.debug('break footer colfmt literal? %s',
                  [c.literal
                   for b in self._breaks if b.footfmts
                   for c in b.footfmts])
        self._break_vals = {}
        self._break_sums = {}

        self._sql = HTML.by_class(body, 'code', 'query')[0].text

    def _parse_colfmts(self, head_row, body_row,
                       all_fields=False, in_footer=False):
        return [
            ColFmt(th=th.text, filler=td.text,
                   literal=(
                       not HTML.has_class(th, 'sum') if in_footer else
                       HTML.has_class(th, 'literal') and not all_fields),
                   blank=in_footer or HTML.has_class(th, 'blank'),
                   field=td.attrib.get('title', None),
                   align=th.attrib.get('align', '')[:1].upper())
            for (th, td)
            in zip(head_row, body_row)]

    def _footfmts(self, name, detail):
        foot_row = HTML.the(detail, 'h:tfoot/h:tr[@class]')
        if foot_row.attrib['class'] != name:
            return None
        return self._parse_colfmts(foot_row, foot_row, in_footer=True)

    def _data(self, connect):
        with run_query(connect, self._sql) as q:
            colnames = [c[0] for c in q.description]
            while 1:
                rows = q.fetchmany()
                if not rows:
                    break
                for row in rows:
                    yield colnames, row

    def pdf_string(self):
        return self.output('', 'S')

    def _start_page(self,
                    large=12, bold='B'):
        self.add_page(orientation=self._orientation)
        self._block(
            self._report_header,
            large, bold, self.white, self.black)
        self._pg_header()

    def _block(self, text, size, style, fg, bg=None):
        self.set_font(self.font, style, size)
        with self.fg_bg(fg, self.white if bg is None else bg):
            # use .text() rather than .cell()?
            self.cell(self.get_string_width(text + ' '),
                      self._h(size), text,
                      fill=1 if bg is not None else 0,
                      ln=self.then_newline)

    @contextmanager
    def fg_bg(self, fg, bg):
        self.set_text_color(fg)
        self.set_fill_color(bg)
        try:
            yield
        finally:
            self.set_text_color(self.black)
            self.set_fill_color(self.white)

    def _h(self, size):
        return size * self.normal_line_height

    def header(self):
        if self._first_line:
            return

        self._pg_header()
        self._show_breaks(0, self._bindings)

    def _pg_header(self,
                   size=11, margin_top=4, margin_bottom=2):
        self._first_line = False
        self.ln(margin_top)
        with self.fg_bg(self.black, self.grey):
            txts = self._eval_fields(bindings=dict(r=RDot(self)),
                                     colfmts=self._pg_colfmts)
            self._row(txts, size,
                      fill=1, margin_bottom=margin_bottom)
        self._detail_header()

    def _detail_header(self,
                       border_top=1, border_bottom=1, margin_bottom=2):
        self.set_font(self.font, self.bold, self.detail_size)
        with self.fg_bg(self.black, self.light_grey):
            self._row([c.th for c in self._detail_colfmts],
                      self.detail_size, fill=1, colfmts=self._detail_colfmts,
                      margin_bottom=margin_bottom,
                      border_top=border_top, border_bottom=border_bottom)

    def _detail(self, rows):
        parity = 0
        with self.fg_bg(self.black, self.light_grey):
            for colnames, vals in rows:
                bindings = dict(zip(colnames, vals))

                break_ix = self._new_breaks(bindings)
                if break_ix is not None:
                    self._do_break_footer()
                    self._show_breaks(break_ix, bindings)

                self._todo('finish value formatting')
                self._todo('money formatting in break footers')
                self.set_font(self.font, self.plain, self.detail_size)
                self._row(self._eval_fields(bindings, self._detail_colfmts),
                          self.detail_size, fill=parity,
                          colfmts=self._detail_colfmts)

                self._update_sums(bindings)

                self._bindings = bindings
                self._page_top = False
                parity = 1 - parity

    def _new_breaks(self, bindings):
        least = None

        for (ix, b) in enumerate(self._breaks):
            newval = [bindings[n] for n in b.key_cols]
            if least is None and newval != self._break_vals.get(b.name):
                least = ix

            if least is not None:
                self._break_vals[b.name] = newval

        return least

    def _show_breaks(self, start, bindings,
                     size=10, style=bold, margin_top=3):
        self.set_font(self.font, style, size)
        for b in self._breaks[start:]:
            txts = self._eval_fields(bindings=bindings,
                                     colfmts=b.colfmts)
            self._row(txts, size, colfmts=b.colfmts,
                      margin_top=margin_top)

    def _update_sums(self, bindings):
        for fmts in [b.footfmts for b in self._breaks if b.footfmts][:1]:
            for f in fmts:
                if not f.literal:
                    self._break_sums[f.field] = (
                        self._break_sums.get(f.field, 0)
                        + bindings[f.field])

    def _do_break_footer(self,
                         style=bold,
                         margin_top=2, border_top=1,
                         margin_bottom=1):
        if not self._break_sums:
            return

        self._todo('get footers to line up')
        for fmts in [b.footfmts for b in self._breaks if b.footfmts][:1]:
            txts = self._eval_fields(bindings=self._break_sums,
                                     colfmts=fmts)
            self.set_font(self.font, style, self.detail_size)
            self._row(txts, self.detail_size, colfmts=fmts,
                      border_top=border_top,
                      margin_top=margin_top,
                      margin_bottom=margin_bottom)
            self._break_sums = {}

    def _eval_fields(self, bindings, colfmts):
        env = dict(bindings.items() + self._fns.items())

        vals = [(' ' * len(c.filler) if c.blank
                 else c.filler) if c.literal
                else _eval(c.field, env)
                for c in colfmts]
        valstrs = [(v.strftime('%m/%d/%Y') if hasattr(v, 'strftime')
                    else str('' if v is None else v))[:len(c.filler)]
                   for (c, v) in zip(colfmts, vals)]
        return valstrs

    def _row(self, txts, size,
             fill=0, colfmts=None,
             margin_top=None, margin_bottom=None,
             border_top=None, border_bottom=None):
        if margin_top:
            self.ln(margin_top)
        if border_top:
            self._hline(border_top)

        cells = zip(txts,
                    [c.filler for c in colfmts] if colfmts else txts,
                    [c.align for c in colfmts] if colfmts
                    else [None] * len(txts))
        #log.debug('_row cells: %s', cells)
        for (txt, w, a) in cells:
            self._todo('constrain _row by right margin')
            self.cell(self.get_string_width(w + ' '), self._h(size),
                      txt + ' ', fill=fill, align=a,
                      ln=self.then_right)
        if fill:
            self.cell(self.right_margin - self.x, self._h(size), fill=1)
        self.ln()
        if border_bottom:
            self._hline(border_bottom)
        if margin_bottom:
            self.ln(margin_bottom)

    def _hline(self, h):
        y = self.y + h / 2
        self.line(self.x, y, self.right_margin, y)
        self.ln(h)

    def _todo(self, what=''):
        self.todos.add(what)


def _abbr_align(s):
    return s[:1].upper()


def _eval(expr, env):
    try:
        return eval(expr, NO_GLOBALS, env)
    except (ValueError, TypeError) as ex:
        log.error('bad field: %s', expr, exc_info=ex)
        return expr


class RDot(object):
    def __init__(self, fpdf):
        self._fpdf = fpdf

    @property
    def pageno(self):
        return str(self._fpdf.page_no())


NO_GLOBALS = {'__builtins__': {}}


def field_functions(cal):
    '''
    >>> from datetime import date
    >>> env = field_functions(lambda: date(2001, 3, 2))
    >>> eval('date()', env)
    datetime.date(2001, 3, 2)
    '''
    def date():
        return cal()

    def stod(s):
        return (datetime.strptime(s, '%Y-%m-%d').date()
                if s and isinstance(s, type('')) else s)

    def format(d, fmt):
        if not d:
            return d
        if not fmt.startswith('!@') or not hasattr(d, 'strftime'):
            raise ValueError((d, fmt))
        return d.strftime(fmt[2:]) if d else d

    def iif(test, t, f):
        return t if test else f

    return dict([(f.__name__, f)
                 for f in [date, stod, iif, format]])


class HTML(object):
    example_ctx = ET.fromstring("""
    <html xmlns='http://www.w3.org/1999/xhtml'>
    <body><h1 class="x y">..</h1></body>
    </html>""")

    namespaces = dict(h='http://www.w3.org/1999/xhtml')

    @classmethod
    def by_class(cls, ctx, tagname, classname):
        '''
        >>> found = HTML.by_class(HTML.example_ctx, 'h1', 'x')
        >>> [(e.tag.split('}')[1], e.attrib['class']) for e in found]
        [('h1', 'x y')]
        '''

        w_class = ctx.findall(
            ".//h:%s[@class]" % tagname,
            namespaces=cls.namespaces)
        return [e for e in w_class
                if cls.has_class(e, classname)]

    @classmethod
    def has_class(cls, elt, classname):
        '''
        >>> HTML.has_class(HTML.example_ctx[0][0], 'x')
        True
        '''
        return classname in elt.get('class', '').split()

    @classmethod
    def the(cls, ctx, expr):
        found = ctx.find(expr, namespaces=cls.namespaces)
        if found is None:
            raise ValueError('cannot find %s in %s' %
                             (expr, ctx.tag))
        return found


@contextmanager
def run_query(connect, sql):
    '''Return a DBI cursor manager executing a SQL query.

    :param connect: () => Connection
    '''
    conn = connect()
    trx = conn.cursor()
    try:
        trx.execute(sql)
        yield trx
    except IOError:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        trx.close()
        conn.close()


def mk_xf(cwd, os_path, open_rd):
    here = ocap.Rd(cwd, os_path, open_rd)
    return Xataface.make(here), here


def mk_connect(getdbi, xf):
    host, user, password, name = xf.dbopts()
    dbi = getdbi()

    def connect():
        return dbi.connect(host=host, user=user, passwd=password, db=name)

    return connect


if __name__ == '__main__':
    def _configure_logging(level=logging.INFO):
        logging.basicConfig(level=level)

    def _with_caps():
        from datetime import date
        from os import path
        from sys import argv, stdout

        def getdbi():
            # TODO: consider pure-python alternative
            import MySQLdb
            return MySQLdb

        xf, here = mk_xf(cwd=path.dirname(__file__),
                         os_path=path,
                         open_rd=lambda n: open(n))

        main(argv[:], stdout, cal=lambda: date.today(),
             connect=mk_connect(getdbi, xf),
             templates=here / 'templates')

    _configure_logging()
    _with_caps()
