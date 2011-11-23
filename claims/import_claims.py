import logging

import xlrd

log = logging.getLogger(__name__)

def main(argv):
    fn = argv[1]
    book = xlrd.open_workbook(fn)

    c = Claim.fromBook(book)
    logging.basicConfig(level=logging.DEBUG)

    log.debug('claim payer contact: %s', c.payer_contact())

    explore(book)


class Claim(object):
    @classmethod
    def fromBook(cls, book):
        sheet = [sheet
                 for sheet in book.sheets()
                 if sheet.name == '1500 -TEMPLATE_Grey '][0]
        return cls(sheet)
        
    def __init__(self, sheet):
        self._s = sheet


    _payer_rc = [(5 + 4 * ln, 168)
                 for ln in xrange(3)]
    def payer_contact(self):
        '''
        >>> [xlrd.cellname(r, c) for r, c in Claim._payer_rc]
        ['FM6', 'FM10', 'FM14']
        '''
        return [self._s.cell_value(r, c)
                for r, c in self._payer_rc]


def explore(book):
    for sheet in book.sheets():
        if not sheet.name.startswith('1500 '):
            continue
        log.debug('sheet: %s hidden? %s', sheet.name, sheet.visibility)
        for rowx in xrange(sheet.nrows):
            log.debug('row: %s', rowx)
            for v in sheet.row_values(rowx):
                if v:
                    log.debug('val: %s [%s]', v, type(v))


if __name__ == '__main__':
    import sys
    main(sys.argv)
