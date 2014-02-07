'''Generate office report from design document and SQL data.

refs:
 - `PyFPDF 1.6 Reference Manual`__
 - `Tutorial`__

__ https://code.google.com/p/pyfpdf/wiki/ReferenceManual
__ https://code.google.com/p/pyfpdf/wiki/Tutorial

'''

from fpdf import FPDF


def main(stdin, stdout):
    '''
    Note `_with_caps()` below for `least-authority style`__.

    __ http://www.madmode.com/2013/python-capability-idioms-part-1.html
    '''
    rpt = OfficeReport()
    rpt.run(report_header=stdin.next(), lines=stdin)
    stdout.write(rpt.pdf_string())
    raise NotImplementedError('database input, detail, breaks, etc.')


class OfficeReport(FPDF):
    font = 'Courier'
    full_line = 0
    then_right, then_newline, then_below = 0, 1, 2
    align_left, align_center, align_right = 'L', 'C', 'R'
    normal_line_height = 1.2

    def __init__(self,
                 orientation='P', units='pt', format='Letter',
                 detail_size=10):
        FPDF.__init__(self, orientation, units, format)
        self.font_size = 10

    def run(self, report_header,
            lines,
            large=12, bold='B'):
        self.add_page()
        self.set_font(self.font, bold, large)
        self.cell(self.full_line, h=large * self.normal_line_height,
                  txt=report_header, ln=self.then_newline)
        self.detail(lines)

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


if __name__ == '__main__':
    def _with_caps(out='tuto1.pdf'):
        from sys import stdin, stdout
        main(stdin, stdout)

    _with_caps()
