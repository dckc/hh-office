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
from sqlalchemy import types, schema, exc, orm

import hh_data2 as db
from cell_spec import CellSpec, user_print_file_spec

log = logging.getLogger(__name__)


def main(argv):
    logging.basicConfig(level=logging.DEBUG)

    if '--report-spec' in argv:
        return rlib_spec(_the_spec())

    if '--find-cells' in argv:
        fn = argv[2]
        book = xlrd.open_workbook(fn, formatting_info=True)
        return find_cells(_the_spec(), book)

    engineurl, files = argv[1], argv[2:]
    engine = create_engine(engineurl)

    if files and files[0] == '--init':
        del files[0]
        init_sql(engine)

    for fn in files:
        log.info('\n\nclaim file: %s', fn)
        book = xlrd.open_workbook(fn, formatting_info=True)
        c = Claim.make(book)
        #explore_claim(log, spec, c)
        log.info('patient name: %s', c.patient_name())
        try:
            c.load(engine)
        except KeyError as ex:
            log.warn('no such client: %s', ex)
        except ReferenceError as ex:
            log.warn('insurance already recorded: %s', ex)
        except (exc.IntegrityError, exc.OperationalError) as ex:
            log.warn('insert failed for %s', fn, exc_info=ex)


def init_sql(engine):
    # is this state-of-the-art for 'ensure the table exists'?
    tables = (db.Diagnosis, db.Procedure, db.Carrier, db.Insurance)

    for cls in reversed(tables):
        try:
            cls.__table__.drop(bind=engine)
        except exc.OperationalError:
            pass

    for cls in tables:
        cls.__table__.create(bind=engine)


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


Session = orm.sessionmaker()


class Claim(object):
    @classmethod
    def make(cls, book):
        sheet = [sheet
                 for sheet in book.sheets()
                 if sheet.name == '1500 -TEMPLATE_Grey '][0]
        return cls(book, sheet)
        
    @classmethod
    def from_contents(cls, contents):
        book = xlrd.open_workbook(file_contents=contents, formatting_info=True)
        return cls.make(book)
        
    def __init__(self, book, sheet):
        self._book = book
        self._data = sheet

    def active(self, rx, cx, n=None):
        xf = self._book.xf_list[self._data.cell_xf_index(rx, cx)]
        out = xf._protection_flag and not xf.protection.cell_locked
        log.debug('active(%s@%s) = %s/%s: %s', n,
                  xlrd.cellname(rx, cx),
                  xf._protection_flag, xf.protection.cell_locked,
                  out)
        return out

    def _where(self, spec, n):
        r, c = field_loc(spec[n])
        for rx in xrange(r - 1, r + 3):
            for cx in xrange(c - 2, c + 2):
                if self.active(rx, cx, n):
                    return rx, cx

    def field(self, n):
        '''
        >>> n1 = ('21.1', 'Diagnosis or Nature of Illness or Injury (Code)')
        >>> n2 = ('21.2', 'Diagnosis or Nature of Illness or Injury (Code)')
        >>> rx, cx = user_print_file_spec[n1].cell
        >>> xlrd.cellname(rx, cx)
        'I157'
        >>> xlrd.cellname(rx, cx + 13)
        'V157'
        >>> rx, cx = user_print_file_spec[n2].cell
        >>> xlrd.cellname(rx, cx)
        'I165'
        '''
        rx, cx = user_print_file_spec[n].cell

        if n[0] in ('21.1', '21.2'):
            dx123 = self._data.cell_value(rx, cx)
            dx56 = self._data.cell_value(rx, cx + 13)
            return '%s.%s' % (dx123, dx56) if dx123 else None

        return self._data.cell_value(rx, cx)


    _payer_rc = [(5 + 4 * ln, 168)
                 for ln in xrange(3)]
    def payer_contact(self):
        '''
        >>> [xlrd.cellname(r, c) for r, c in Claim._payer_rc]
        ['FM6', 'FM10', 'FM14']
        '''
        return dict(zip(('name', 'address', 'city_st_zip'),
                        [self._data.cell_value(r, c)
                         for r, c in self._payer_rc]))

    def patient_name(self):
        return self.field(('2', "Patient's Name (Last, First, MI)"))

    def load(self, engine):
        '''
        @raises KeyError if there is no client by the given name,
                ReferenceError if the named client already has
                an Insurance record.
        '''
        session = Session(bind=engine)

        get = self.field

        client = self.client(session)

        if session.query(db.Insurance).filter_by(Client_id=client.id).first():
            raise ReferenceError

        payer = self.load_carrier(session)

        def which(fnum, choices=None, xlate=None, paren=None):
            return pick(get, user_print_file_spec.keys(),
                        fnum, choices, xlate, paren)

        def which_sex(fnum):
            return which(fnum, xlate={'Sex-Male': 'M', 'Sex-Female': 'F'})

        def get_date(fnum, label, aux=None):
            return _yymmdd(
                *[get((fnum, "%s %s(%s)" % (
                    label, aux + ' ' if aux and part != 'Year' else '',  part)))
                  for part in ('Year', 'Month', 'Day')])

        def get_phone(fnum, prefix):
            acode, rest = [int(x) if type(x) is type(1.0) else x
                           for x in
                           [get((fnum, "%s %s" % (prefix, part)))
                            for part in ("Area Code", "Phone Number")]]
            
            return "%s %s" % (acode, rest) if acode else rest
            
        dx = self.load_dx(session)

        policy = db.Insurance(
            carrier=payer,
            payer_type=which('1'),
            id_number=get(('1a', "Insured's ID Number")),
            client=client,
            patient_sex=which_sex('3'),
            insured_name=get(('4', 'Insured Name (Last, First, MI)')),
            patient_rel=which('6', paren=True),
            insured_address=get(('7', "Insured's Address")),
            insured_city=get(('7', "Insured's City")),
            insured_state=get(('7', "Insured's State")),
            insured_zip=_zip(get(('7', "Insured's ZIP Code"))),
            insured_phone=get_phone('7', "Insured's"),
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
            insured_dob=get_date('11a', "Insured's Date of Birth"),
            insured_sex=which_sex('11a'),
            dx1=dx[0],
            dx2=dx[1],
            )

        # dunno why this doesn't work, but it gives:
        # sqlalchemy.exc.ProgrammingError: (ProgrammingError) (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ') WHERE `Client`.id = 171' at line 1") 'UPDATE `Client` SET `DOB`=%s WHERE `Client`.id = %s' ((datetime.date(1987, 7, 31),), 171L)
        #client.DOB = get_date('3', "Patient's Birth")

        ct = db.Client.__table__
        session.execute(ct.update().\
                        where(ct.c.id == client.id).\
                        values(DOB=get_date('3', "Patient's Birth", 'Date'),
                               address=get(('5', "Patient's Address")),
                               city=get(('5', "Patient's City")),
                               state=get(('5', "Patient's State")),
                               zip=str(int(get(('5', "Patient's ZIP Code")))),
                               patient_phone=get_phone('5', "Patient's")))

        session.add(policy)
        session.commit()
        return policy


    def load_carrier(self, session):
        payer_contact = self.payer_contact()

        try:
            payer = session.query(db.Carrier).filter_by(
                name=payer_contact['name']).one()
        except orm.exc.NoResultFound, ex:
            payer = db.Carrier(**payer_contact)
            session.add(payer)
        return payer

    def client(self, session):
        patient_name = self.patient_name()
        try:
            return session.query(db.Client).filter_by(
                name=patient_name).one()
        except orm.exc.NoResultFound:
            raise KeyError, patient_name

    def load_dx(self, session):
        get = self.field
        dxs = [get((f, "Diagnosis or Nature of Illness or Injury (Code)"))
               for f in (('21.1', '21.2'))]
        for dx in dxs:
            if not dx:
                continue
            if not session.query(db.Diagnosis).filter_by(icd9=dx).first():
                session.add(db.Diagnosis(icd9=dx))
        log.debug('dxs: %s', dxs)
        return dxs


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


def find_cells(spec, book):
    from pprint import pprint
    
    c = Claim.make(book, spec)
    xls_spec = dict([(k, CellSpec._make(v + (c._where(k),)))
                     for k, v in spec.items()])
    pprint(xls_spec)


if __name__ == '__main__':
    import sys
    main(sys.argv)
