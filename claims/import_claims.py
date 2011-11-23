from collections import namedtuple
import csv
import logging

import xlrd

log = logging.getLogger(__name__)

def main(argv):
    logging.basicConfig(level=logging.INFO)

    specfn, fn = argv[1:3]
    spec = make_spec(open(specfn))

    book = xlrd.open_workbook(fn, formatting_info=True)

    c = Claim.make(book, spec)

    for k in sorted(spec,
                    key=lambda(fs): (spec[fs].field,
                                     spec[fs].line,
                                     spec[fs].columns)):
        log.debug('field %s: %s %s %s', k,
                 (spec[k].line, spec[k].columns[0]),
                 field_loc(spec[k]),
                 xlrd.cellname(*field_loc(spec[k])))
        if c.field(k):
            log.info('field %s: <%s>', k, c.field(k))

    log.info('patient name: %s', c.patient_name())
    log.info('claim payer contact: %s', c.payer_contact())


FieldSpec = namedtuple('FieldSpec',
                       'line field literal field_type bytes columns')


def make_spec(fp):
    return dict([((r['FIELD'], r['LITERAL']),
                  FieldSpec(int(r['LINE']),
                            grok_field(r['FIELD']),
                            r['LITERAL'],
                            r['FIELD TYPE'],
                            int(r['BYTES']),
                            [int(x) for x in r['COLUMNS'].split('-')]))
                 for r in csv.DictReader(fp)
                 if r['COLUMNS']])


def grok_field(f):
    '''
    >>> grok_field('1')
    (1, '1')
    >>> grok_field('1a')
    (1, '1a')
    >>> grok_field('10a')
    (10, '10a')
    '''
    if f:
        return int(f[:2 if f[1:2].isdigit() else 1]), f
    else:
        return ()


def _fs(line):
    r'''
    >>> _fs("""3,1a,"Insured's ID Number",A/N,29,50-78,""")
    FieldSpec(line=3, field=(1, '1a'), literal="Insured's ID Number", field_type='A/N', bytes=29, columns=[50, 78])

    >>> _fs("""5,3,Sex-Male,M,1,42,""")
    FieldSpec(line=5, field=(3, '3'), literal='Sex-Male', field_type='M', bytes=1, columns=[42])

    '''
    # ' un-confuse emacs
    lines = ['LINE,FIELD,LITERAL,"FIELD TYPE",BYTES,COLUMNS,', line]
    spec = make_spec(lines)
    return spec[spec.keys()[0]]


def _t(line):
    fs = _fs(line)
    return field_loc(fs)


def field_loc(fs):
    r'''
    >>> _t('3,1,Medicare,M,1,1,')
    (32, 4)

    >>> _t("""7,5,"Patient's Address",A/N,28,01-28,""")
    (48, 4)

    '''
    # ' un-confuse emacs
    r = fs.line * 4 + 20
    c = fs.columns[0] * 3 + 1
    return r, c


class Claim(object):
    @classmethod
    def make(cls, book, spec):
        sheet = [sheet
                 for sheet in book.sheets()
                 if sheet.name == '1500 -TEMPLATE_Grey '][0]
        return cls(book, sheet, spec)
        
    def __init__(self, book, sheet, spec):
        self._book = book
        self._data = sheet
        self._spec = spec

    def active(self, rx, cx):
        xf = self._book.xf_list[self._data.cell_xf_index(rx, cx)]
        out = xf._protection_flag and not xf.protection.cell_locked
        log.debug('active(%s) = %s/%s: %s',
                  xlrd.cellname(rx, cx),
                  xf._protection_flag, xf.protection.cell_locked,
                  out)
        return out

    def field(self, n):
        r, c = field_loc(self._spec[n])
        cv = self._data.cell_value
        for rx in xrange(r - 1, r + 3):
            for cx in xrange(c - 2, c + 2):
                if self.active(rx, cx):
                    return cv(rx, cx)


    _ptn_rc = (39, 4)
    def patient_name(self):
        '''
        >>> xlrd.cellname(*Claim._ptn_rc)
        'E40'
        '''
        return self._data.cell_value(*self._ptn_rc)

    _payer_rc = [(5 + 4 * ln, 168)
                 for ln in xrange(3)]
    def payer_contact(self):
        '''
        >>> [xlrd.cellname(r, c) for r, c in Claim._payer_rc]
        ['FM6', 'FM10', 'FM14']
        '''
        return [self._data.cell_value(r, c)
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
