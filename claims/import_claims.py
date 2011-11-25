'''import_claims -- import patien insurance info from .xls to SQL

Usage::
  $ python import_claims.py sqlite:///,ins.db ,data/*.xls

'''

from collections import namedtuple
import csv
import logging
import datetime
import os

import xlrd
from sqlalchemy import MetaData, Table, Column, create_engine
from sqlalchemy import types, schema, exc


log = logging.getLogger(__name__)


def main(argv):
    logging.basicConfig(level=logging.INFO)

    spec = _the_spec()
    if '--report-spec' in argv:
        return rlib_spec(spec)

    engineurl, files = argv[1], argv[2:]
    engine = create_engine(engineurl)

    if files and files[0] == '--init':
        del files[0]
        init_sql(engine)

    for fn in files:
        log.info('claim file: %s', fn)
        book = xlrd.open_workbook(fn, formatting_info=True)
        c = Claim.make(book, spec)
        #explore_claim(log, spec, c)
        log.info('patient name: %s',
                 c.field(('2', "Patient's Name (Last, First, MI)")))
        try:
            engine.execute(c.insert())
        except (exc.IntegrityError, exc.OperationalError) as ex:
            log.warn('insert failed for %s', fn, exc_info=ex)


def init_sql(engine):
    # is this state-of-the-art for 'ensure the table exists'?
    try:
        HealthInsurance.drop(bind=engine)
    except exc.OperationalError:
        pass
    HealthInsurance.create(bind=engine)


def _the_spec(specfn='user_print_file_spec.csv'):
    return make_spec(open(os.path.join(os.path.dirname(__file__), specfn)))


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

    def active(self, rx, cx, n=None):
        xf = self._book.xf_list[self._data.cell_xf_index(rx, cx)]
        out = xf._protection_flag and not xf.protection.cell_locked
        log.debug('active(%s@%s) = %s/%s: %s', n,
                  xlrd.cellname(rx, cx),
                  xf._protection_flag, xf.protection.cell_locked,
                  out)
        return out

    def field(self, n):
        r, c = field_loc(self._spec[n])
        cv = self._data.cell_value
        for rx in xrange(r - 1, r + 3):
            for cx in xrange(c - 2, c + 2):
                if self.active(rx, cx, n):
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

        def which(fnum, choices=None, xlate=None, paren=None):
            return pick(get, self._spec.keys(), fnum, choices, xlate, paren)

        pn, pa, pcsz = self.payer_contact()

        return HealthInsurance.insert().values(
            payer_name=pn,
            payer_address=pa,
            payer_city_st_zip=pcsz,
            payer_type=which('1'),
            id_number=get(('1a', "Insured's ID Number")),
            patient_name=get(('2', "Patient's Name (Last, First, MI)")),
            patient_dob=_yymmdd(get(('3', "Patient's Birth (Year)")),
                                get(('3', "Patient's Birth Date (Month)")),
                                get(('3', "Patient's Birth Date (Day)"))),
            patient_sex=which('3', xlate={'Sex-Male': 'M', 'Sex-Female': 'F'}),
            insured_name=get(('4', 'Insured Name (Last, First, MI)')),
            patient_address=get(('5', "Patient's Address")),
            patient_city=get(('5', "Patient's City")),
            patient_state=get(('5', "Patient's State")),
            patient_zip=str(int(get(('5', "Patient's ZIP Code")))),
            patient_acode=get(('5', "Patient's Area Code")),
            patient_phone=get(('5', "Patient's Phone Number")),
            patient_rel=which('6', paren=True),
            insured_address=get(('7', "Insured's Address")),
            insured_city=get(('7', "Insured's City")),
            insured_state=get(('7', "Insured's State")),
            insured_zip=_zip(get(('7', "Insured's ZIP Code"))),
            insured_acode=get(('7', "Insured's Area Code")),
            insured_phone=get(('7', "Insured's Phone Number")),
            patient_status=which('8', choices=(
                "Patient Status (Single)",
                "Patient Status (Married)",
                "Patient Status (Other)"), paren=True),
            patient_status2=which('8', choices=(
                "Patient Status (Employed)",
                "Patient Status (Full Time Student)",
                "Patient Status (Part Time Student)"), paren=True),
            insured_policy=(
                get(('11', "Insured's Policy, Group or FECA Number"))
                or None),  # don't store ''
            insured_dob=_yymmdd(
                get(('11a', "Insured's Date of Birth (Year)")),
                get(('11a', "Insured's Date of Birth (Month)")),
                get(('11a', "Insured's Date of Birth (Day)"))),
            insured_sex=which('11a',
                              xlate={'Sex-Male': 'M', 'Sex-Female': 'F'})
            )

def _yymmdd(yy, mm, dd):
    if not (yy and mm and dd):
        return None
    y = int(yy)
    return datetime.date(int(2000 + y if y < 50 else 1900 + y),
                         int(mm), int(dd))


def _zip(z):
    if not z: return None
    return str(int(z))


def pick(get, keys, fnum, choices=None, xlate=None, paren=False):
    '''
    >>> get = {('8', "abc"): 'x'}.get
    >>> pick(get, [('8', "abc"), ('8', "def")], '8')
    'abc'

    >>> spec = _the_spec()
    >>> pick({('8', "Patient Status (Employed)"): 'x'}.get, spec.keys(),
    ...        '8', choices=(
    ...            "Patient Status (Employed)",
    ...            "Patient Status (Full Time Student)",
    ...            "Patient Status (Part Time Student)"), paren=True)
    'Employed'
    '''
    if xlate:
        choices = xlate.keys()

    fields = [(num, label) for num, label in keys
              if num == fnum
              and (choices is None or label in choices)]

    vals = [label for num, label in fields
            if get((num, label)) in ('x', 'X')]
    if vals:
        val = vals[0]
        if paren:
            if choices is None:
                choices = [label for num, label in fields]
            xlate = dict([(txt,
                           txt[txt.index('(')+1:txt.index(')')])
                          for txt in choices])
        return val if xlate is None else xlate[val]
    else:
        return None


Meta = MetaData()
HealthInsurance = Table(
    'health_insurance', Meta,
    Column('id', types.Integer, primary_key=True, nullable=False),
    Column('payer_name', types.String(50), nullable=False),
    Column('payer_address', types.String(50), nullable=False),
    Column('payer_city_st_zip', types.String(50), nullable=False),
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
    Column('patient_acode', types.String(3)),
    Column('patient_phone', types.String(7)),
    # Field 6
    Column('patient_rel', types.Enum('Self', 'Spouse', 'Child', 'Other'),
           nullable=False),
    # Field 7
    Column('insured_address', types.String(30), nullable=False),
    Column('insured_city', types.String(24), nullable=False),
    Column('insured_state', types.String(3), nullable=False),
    Column('insured_zip', types.String(12), nullable=False),
    Column('insured_acode', types.String(3)),
    Column('insured_phone', types.String(7)),
    # Field 8
    Column('patient_status', types.Enum('Single', 'Married', 'Other')),
    Column('patient_status2', types.Enum('Employed',
                                         'Full Time Student',
                                         'Part Time Student')),
    # skip 10
    # Field 11
    Column('insured_policy', types.String(30)),
    # Field 11a
    Column('insured_dob', types.Date),
    Column('insured_sex', types.Enum('M', 'F')),
    # 12, 13 are blank; skip 14-18; 19 is reserved
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


def rlib_spec(spec):
    line = 1
    col = 1
    print "  <Line> <!-- %d -->" % line
    for fs in sorted(spec.values(), key=lambda e: (e.line, e.columns)):
        if not fs.field: continue

        while line < fs.line:
            print "  </Line>"
            line += 1
            col = 1
            print "  <Line> <!-- %d -->" % line


        width = fs.columns[0] - col
        if width > 0:
            col += width
            print "    <literal width='%d' /> <!-- col %d -->" % (width, col)

        width = fs.columns[-1] - fs.columns[0] + 1
        print "    <field width='%d' value='\"%s\"' align='%s'/>" % (
            width, fs.literal, ('right' if fs.field_type == 'N'
                             else 'left'))
        col += width
    print "  </Line>"


if __name__ == '__main__':
    import sys
    main(sys.argv)
