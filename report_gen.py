# cribbed Minimal Example
# from
# https://code.google.com/p/pyfpdf/wiki/Tutorial
#
# adapted to least-authority style
# http://www.madmode.com/2013/python-capability-idioms-part-1.html
from fpdf import FPDF


def main(save):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Hello World!')
    save(pdf.output('', 'S'))


if __name__ == '__main__':
    def _with_caps(out='tuto1.pdf'):
        main(save=lambda x: open(out, 'w').write(x))

    _with_caps()
