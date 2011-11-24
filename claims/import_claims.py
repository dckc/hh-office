from collections import namedtuple
import csv
import logging
import datetime

import xlrd
from sqlalchemy import MetaData, Table, Column, types, schema, create_engine


log = logging.getLogger(__name__)


def main(argv):
    logging.basicConfig(level=logging.INFO)

    specfn, files = argv[1], argv[2:]
    spec = make_spec(open(specfn))

    for fn in files:
        book = xlrd.open_workbook(fn, formatting_info=True)
        c = Claim.make(book, spec)
        explore_claim(log, spec, c)


def explore_claim(log, spec, c):
    from pprint import pformat

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

    log.info('claim payer contact: %s', c.payer_contact())
    dml = c.insert()
    log.info('insert: \n%s', pformat(dml.compile().params))


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


    _payer_rc = [(5 + 4 * ln, 168)
                 for ln in xrange(3)]
    def payer_contact(self):
        '''
        >>> [xlrd.cellname(r, c) for r, c in Claim._payer_rc]
        ['FM6', 'FM10', 'FM14']
        '''
        return [self._data.cell_value(r, c)
                for r, c in self._payer_rc]

    def insert(self):
        get = self.field

        def which(fnum):
            return [label for num, label in self._spec.keys()
                    if num == fnum
                    and get((num, label)) == 'X'][0]

        pn, pa, pcsz = self.payer_contact()

        return HealthInsurance.insert().values(
            payer_name=pn,
            payer_address=pa,
            payer_city_st_zip=pcsz,
            payer_type=which('1'),
            id_number=get(('1a', "Insured's ID Number")),
            patient_name=get(('2', "Patient's Name (Last, First, MI)")),
            patient_dob=datetime.date(
                _yy(get(('3', "Patient's Birth (Year)"))),
                int(get(('3', "Patient's Birth Date (Month)"))),
                int(get(('3', "Patient's Birth Date (Day)")))),
            patient_sex={'Sex-Male': 'M', 'Sex-Female': 'F'}[which('3')],
            insured_name=get(('4', 'Insured Name (Last, First, MI)')),
            patient_address=get(('5', "Patient's Address")),
            patient_city=get(('5', "Patient's City")),
            patient_state=get(('5', "Patient's State")),
            patient_zip=str(int(get(('5', "Patient's ZIP Code")))),
            patient_rel=_paren(which('6')),
            insured_address=get(('7', "Insured's Address")),
            insured_city=get(('7', "Insured's City")),
            insured_state=get(('7', "Insured's State")),
            insured_zip=str(int(get(('7', "Insured's ZIP Code")))),
            )

def _yy(yy):
    return int(2000 + yy if yy < 50 else 1900 + yy)


def _paren(txt):
    '''
    >>> paren('abc (def) ghi')
    'def'
    '''
    return txt[txt.index('(')+1:txt.index(')')]


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



Meta = MetaData()
HealthInsurance = Table(
    'health_insurance', Meta,
    Column('id', types.Integer, primary_key=True, nullable=False),
    Column('payer_name', types.String(30), nullable=False),
    Column('payer_address', types.String(30), nullable=False),
    Column('payer_city_st_zip', types.String(40), nullable=False),
    # Field 1 from user_print_file_spec.csv
    Column('payer_type', types.Enum('Medicare',
                                    'Medicaid',
                                    'Group Health Plan',
                                    'Other'), nullable=False),
    Column('id_number', types.String(30), nullable=False),
    # Field 2
    Column('patient_name', types.String(30), nullable=False),
    # Field 3
    Column('patient_dob', types.Date, nullable=False),
    Column('patient_sex', types.Enum('M', 'F'), nullable=False),
    # Field 4
    Column('insured_name', types.String(30), nullable=False),
    # Field 5
    Column('patient_address', types.String(30), nullable=False),
    Column('patient_city', types.String(24), nullable=False),
    Column('patient_state', types.String(3), nullable=False),
    Column('patient_zip', types.String(12), nullable=False),
    # Field 6
    Column('patient_rel', types.Enum('Self', 'Spouse', 'Child', 'Other'),
           nullable=False),
    # Field 7
    Column('insured_address', types.String(30), nullable=False),
    Column('insured_city', types.String(24), nullable=False),
    Column('insured_state', types.String(3), nullable=False),
    Column('insured_zip', types.String(12), nullable=False),
    # skip 10, 11; 12, 13 are blank; skip 14-18; 19 is reserved
    # 20 is computed per-claim
    # Field 21
    Column('dx1', types.String(8)),
    Column('dx2', types.String(8)),
    Column('dx3', types.String(8)),
    Column('dx4', types.String(8))
    )

def _test_schema_sql():
    '''
    >>> ddl = schema.CreateTable(HealthInsurance)
    >>> 'CREATE TABLE' in str(ddl)
    True
    
    >>> 'insured_address' in  str(ddl)
    True

    '''
    pass


if __name__ == '__main__':
    import sys
    main(sys.argv)
