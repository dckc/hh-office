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


def main(argv, stdin, stdout, open_arg):
    '''
    Note `_with_caps()` below for `least-authority style`__.

    __ http://www.madmode.com/2013/python-capability-idioms-part-1.html
    '''
    design_doc = argv[1]
    rpt = OfficeReport.make(open_arg(design_doc))
    rpt.run(lines=stdin)
    stdout.write(rpt.pdf_string())
    raise NotImplementedError('database input, detail, breaks, etc.')


class OfficeReport(FPDF):
    portrait, landscape = 'P', 'L'
    font = 'Courier'
    plain = ''
    full_line = 0
    then_right, then_newline, then_below = 0, 1, 2
    align_left, align_center, align_right = 'L', 'C', 'R'
    normal_line_height = 1.2
    black, grey, white = 0, 0xd0, 0xff

    def __init__(self, design,
                 unit='pt', format='Letter',
                 detail_size=10):
        FPDF.__init__(self, unit=unit, format=format)
        self.design = design
        self._first_line = True

    @classmethod
    def make(cls, fp):
        return cls(ET.parse(fp))

    def run(self, lines):
        self._start_page()
        self._detail(lines)

    def pdf_string(self):
        return self.output('', 'S')

    def _start_page(self,
                    large=12, bold='B'):
        self.add_page(
            orientation=(
                self.landscape
                if HTML.by_class(self.design, 'body', 'landscape')
                else self.portrait))

        hd_txt = HTML.by_class(self.design, 'h1', 'ReportHeader')[0].text
        self.set_font(self.font, bold, large)
        with self.fg_bg(self.white, self.black):
            self.cell(self.get_string_width(hd_txt + ' '),
                      self._h(large), hd_txt,
                      fill=1, ln=self.then_newline)
        self._header()

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

    def _detail(self, lines,
                default_size=10,
                sizes=[('small-print', 8),
                       ('medium-print', 9)]):
        explicit_sizes = [sz for (n, sz) in sizes
                          if HTML.by_class(self.design, 'body', n)]
        self.detail_size = (explicit_sizes[-1] if explicit_sizes
                            else default_size)
        self.set_font(self.font, self.plain, self.detail_size)

        for line in lines:
            self.write(self._h(self.detail_size), line)
            self.ln()

    def header(self):
        if self._first_line:
            return

        self._header()

    def _header(self,
                size=11, border_top=4, border_bottom=2):
        '''
      <HorizontalLine size="4" bgcolor="'white'"/>
      <Line fontSize="11" bgcolor="'0xd0d0d0'" color="'black'">
        <literal width="2"/>
        <xsl:apply-templates mode="Line" />
      </Line>
      <HorizontalLine size="2" bgcolor="'white'" />
        '''
        self._first_line = False
        pghd = HTML.by_class(self.design, 'h2', 'PageHeader')[0]
        self._hline(border_top)
        with self.fg_bg(self.black, self.grey):
            self._line(pghd, size, fill=1)
        self._hline(border_bottom)

    def _hline(self, h,
               right_margin=7.5 * 72):
        y = self.y + h / 2
        self.line(self.x, y, right_margin, y)
        self.ln(h)

    def _line(self, ctx, size,
              fill=0):
        self.set_font(self.font, self.plain, size)

        for elt in ctx:
            if HTML.has_class(elt, 'literal'):
                txt = (' ' * len(elt.text) if HTML.has_class(elt, 'blank')
                       else elt.text)
                self.cell(self.get_string_width(txt + ' '), self._h(size),
                          txt, fill=fill)
            else:
                self.todo('field')
        self.ln()

    @classmethod
    def todo(cls, what=''):
        #@@raise NotImplementedError
        import sys
        print >>sys.stderr, "TODO!!", what

    @classmethod
    def fontSize(cls, classname,
                 default=10):
        return cls.todo() if classname else default


class HTML(object):
    example_ctx = ET.fromstring("""
    <html xmlns='http://www.w3.org/1999/xhtml'>
    <body><h1 class="x y">..</h1></body>
    </html>""")

    @classmethod
    def by_class(cls, ctx, tagname, classname):
        '''
        >>> found = HTML.by_class(HTML.example_ctx, 'h1', 'x')
        >>> [(e.tag.split('}')[1], e.attrib['class']) for e in found]
        [('h1', 'x y')]
        '''

        w_class = ctx.findall(
            ".//h:%s[@class]" % tagname,
            namespaces=dict(h='http://www.w3.org/1999/xhtml'))
        return [e for e in w_class
                if cls.has_class(e, classname)]

    @classmethod
    def has_class(cls, elt, classname):
        '''
        >>> HTML.has_class(HTML.example_ctx[0][0], 'x')
        True
        '''
        return classname in elt.attrib['class'].split()


if __name__ == '__main__':
    def _with_caps(out='tuto1.pdf'):
        from sys import argv, stdin, stdout

        def open_arg(n):
            if n not in argv:
                raise IOError
            return open(n)

        main(argv[:], stdin, stdout, open_arg)

    _with_caps()
