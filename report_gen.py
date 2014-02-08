'''Generate office report from design document and SQL data.

refs:
 - `PyFPDF 1.6 Reference Manual`__
 - `Tutorial`__

__ https://code.google.com/p/pyfpdf/wiki/ReferenceManual
__ https://code.google.com/p/pyfpdf/wiki/Tutorial

'''

from contextlib import contextmanager
from xml.etree import ElementTree as ET

from fpdf import FPDF


def main(argv, stdin, stdout, open_arg, cal):
    '''
    Note `_with_caps()` below for `least-authority style`__.

    __ http://www.madmode.com/2013/python-capability-idioms-part-1.html
    '''
    design_doc = argv[1]
    rpt = OfficeReport.make(open_arg(design_doc), cal)
    rpt.run(lines=stdin)
    stdout.write(rpt.pdf_string())
    raise NotImplementedError('database input, detail, breaks, etc.')


class OfficeReport(FPDF):
    portrait, landscape = 'P', 'L'
    font = 'Courier'
    plain, bold = '', 'B'
    full_line = 0
    then_right, then_newline, then_below = 0, 1, 2
    align_left, align_center, align_right = 'L', 'C', 'R'
    normal_line_height = 1.2
    black, grey, dark_grey, white = 0, 0xd0, 0xe5, 0xff

    def __init__(self, design, fns,
                 unit='pt', format='Letter',
                 detail_size=10):
        FPDF.__init__(self, unit=unit, format=format)
        self.design = design
        self._fns = fns
        self._first_line = True

    @classmethod
    def make(cls, fp, cal):
        return cls(ET.parse(fp), field_functions(cal))

    def run(self, lines):
        self._start_page()
        self._detail(lines)

    def pdf_string(self):
        return self.output('', 'S')

    def _start_page(self,
                    large=12, bold='B',
                    default_size=10,
                    sizes=[('small-print', 8),
                           ('medium-print', 9)]):
        body = HTML.by_class(self.design, 'body', 'rlib')[0]
        self.add_page(
            orientation=(
                self.landscape
                if HTML.has_class(body, 'landscape')
                else self.portrait))

        explicit_sizes = [sz for (n, sz) in sizes
                          if HTML.has_class(body, n)]
        self.detail_size = (explicit_sizes[-1] if explicit_sizes
                            else default_size)

        self._block(
            HTML.by_class(body, 'h1', 'ReportHeader')[0].text,
            large, bold, self.white, self.black)
        self._pg_header()

    def _block(self, text, size, style, fg, bg=None):
        self.set_font(self.font, style, size)
        with self.fg_bg(fg, self.white if bg is None else bg):
            # TODO: use .text() rather than .cell()?
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

    def _pg_header(self,
                   size=11, margin_top=4, margin_bottom=2):
        self._first_line = False
        pghd = HTML.by_class(self.design, 'h2', 'PageHeader')[0]
        self.ln(margin_top)
        with self.fg_bg(self.black, self.grey):
            self._line(pghd, size, fill=1)
        self.ln(margin_bottom)
        self._detail_header()

    def _detail_header(self,
                       border_top=1, border_bottom=1, margin_bottom=2):
        detail = HTML.by_class(self.design, "table", 'Detail')[0]
        texts = [th.text
                 for th in HTML.the(detail, "h:thead/h:tr[1]")]
        self._widths = [td.text
                        for td in HTML.the(detail, "h:tbody/h:tr[1]")]
        self._aligns = [th.attrib.get('align', '')[:1].upper()
                        for th in HTML.the(detail, "h:thead/h:tr[1]")]
        self.set_font(self.font, self.bold, self.detail_size)
        with self.fg_bg(self.black, self.dark_grey):
            self._row(texts, self.detail_size, fill=1,
                      widths=self._widths, aligns=self._aligns,
                      margin_bottom=margin_bottom,
                      border_top=border_top, border_bottom=border_bottom)

    def _line(self, ctx, size,
              fill=0):
        env = dict(r=RDot(self))
        env.update(self._fns)

        self.set_font(self.font, self.plain, size)

        txts = [
            ((' ' * len(elt.text) if HTML.has_class(elt, 'blank')
              else elt.text)
             if HTML.has_class(elt, 'literal')
             else eval(elt.attrib['title'], {}, env))
            for elt in ctx]
        self._row(txts, size, fill)

    def _detail(self, lines):
        self.set_font(self.font, self.plain, self.detail_size)

        for line in lines:
            texts = line.split(',')  # @@TODO: real csv parser
            self._row(texts, self.detail_size,
                      widths=self._widths, aligns=self._aligns)

    def _row(self, txts, size,
             fill=0, widths=None, aligns=None,
             margin_top=None, margin_bottom=None,
             border_top=None, border_bottom=None):
        if margin_top:
            self.ln(margin_top)
        if border_top:
            self._hline(border_top)
        for (txt, w, a) in zip(txts,
                               widths or txts,
                               aligns or [None] * len(txts)):
            self.cell(self.get_string_width(w + ' '), self._h(size),
                      txt, fill=fill, align=a)
        self.ln()
        if border_bottom:
            self._hline(border_bottom)
        if margin_bottom:
            self.ln(margin_bottom)

    def _hline(self, h,
               right_margin=7.5 * 72):
        y = self.y + h / 2
        self.line(self.x, y, right_margin, y)
        self.ln(h)

    @classmethod
    def _todo(cls, what=''):
        #@@raise NotImplementedError
        import sys
        print >>sys.stderr, "TODO!!", what


class RDot(object):
    def __init__(self, fpdf):
        self._fpdf = fpdf

    @property
    def pageno(self):
        return str(self._fpdf.page_no())


def field_functions(cal):
    '''
    >>> from datetime import date
    >>> env = field_functions(lambda: date(2001, 3, 2))
    >>> eval('date()', env)
    '03/02/2001'
    '''
    def date():
        return cal().strftime('%02m/%02d/%04Y')

    return dict([(f.__name__, f)
                 for f in [date]])


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
        return classname in elt.attrib['class'].split()

    @classmethod
    def the(cls, ctx, expr):
        found = ctx.find(expr, namespaces=cls.namespaces)
        if found is None:
            raise ValueError('cannot find %s in %s' %
                             (expr, ctx.tag))
        return found


if __name__ == '__main__':
    def _with_caps(out='tuto1.pdf'):
        from sys import argv, stdin, stdout
        from datetime import date

        def open_arg(n):
            if n not in argv:
                raise IOError
            return open(n)

        main(argv[:], stdin, stdout, open_arg,
             cal=lambda: date.today())

    _with_caps()
