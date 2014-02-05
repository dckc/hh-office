# Minimal Example
# from
# https://code.google.com/p/pyfpdf/wiki/Tutorial
from fpdf import FPDF

pdf=FPDF()
pdf.add_page()
pdf.set_font('Arial','B',16)
pdf.cell(40,10,'Hello World!')
pdf.output('tuto1.pdf','F')
