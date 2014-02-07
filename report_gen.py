'''Generate office report from design document and SQL data.

refs:
 - `PyFPDF 1.6 Reference Manual`__
 - `Tutorial`__

__ https://code.google.com/p/pyfpdf/wiki/ReferenceManual
__ https://code.google.com/p/pyfpdf/wiki/Tutorial

'''

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
    full_line = 0
    then_right, then_newline, then_below = 0, 1, 2
    align_left, align_center, align_right = 'L', 'C', 'R'
    normal_line_height = 1.2

    def __init__(self, design,
                 unit='pt', format='Letter',
                 detail_size=10):
        FPDF.__init__(self, unit=unit, format=format)
        self.font_size = 10
        self.design = design

    @classmethod
    def make(cls, fp):
        return cls(ET.parse(fp))

    def run(self, lines):
        self.start_page()
        self.detail(lines)

    def start_page(self,
                   large=12, bold='B'):
        self.add_page(
            orientation=(
                self.landscape
                if HTML.by_class(self.design, 'body', 'landscape')
                else self.portrait))

        hd_txt = HTML.by_class(self.design, 'h1', 'ReportHeader')[0].text
        self.set_font(self.font, bold, large)
        self.cell(self.full_line, h=large * self.normal_line_height,
                  txt=hd_txt, ln=self.then_newline)

    def detail(self, lines):
        self.set_font(self.font, '', self.font_size)
        for line in lines:
            self.cell(self.full_line, self.font_size * self.normal_line_height,
                      txt=line, ln=self.then_newline)

    def header(self):
        pass

    def pdf_string(self):
        return self.output('', 'S')

    @classmethod
    def todo(cls):
        raise NotImplementedError

    @classmethod
    def fontSize(cls, classname,
                 default=10):
        return cls.todo() if classname else default


class HTML(object):
    r'''
    >>> ctx = ET.fromstring('<body><h1 class="x y">..</h1></body>')
    >>> [(e.tag, e.attrib['class']) for e in HTML.by_class(ctx, 'h1', 'x')]
    [('h1', 'x y')]
    '''
    @classmethod
    def by_class(cls, ctx, tagname, classname):
        w_class = ctx.findall(
            ".//h:%s[@class]" % tagname,
            namespaces=dict(h='http://www.w3.org/1999/xhtml'))
        return [e for e in w_class
                if classname in e.attrib['class'].split()]


if __name__ == '__main__':
    def _with_caps(out='tuto1.pdf'):
        from sys import argv, stdin, stdout

        def open_arg(n):
            if n not in argv:
                raise IOError
            return open(n)

        main(argv[:], stdin, stdout, open_arg)

    _with_caps()
