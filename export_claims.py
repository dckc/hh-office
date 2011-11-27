''' export_claims -- export claims in CSV format

https://sfreeclaims.anvicare.com/docs/forms/Reference-CSV%20Specifications.txt
'''

from os import path, environ
import ConfigParser

import MySQLdb

def _test_main(ini='conf.ini'):
    import sys

    here = path.dirname(__file__)
    opts = PrefixConfig(File(here, ini), '[DEFAULT]').opts()
    outfn = sys.argv[1]

    def start_response(r, hdrs):
        print r
        print hdrs

    content = run_report(start_response, opts)
    outfp = open(outfn, 'w')
    for part in content:
        outfp.write(part)


class PrefixConfig(object):
    '''work-around: xataface needs options before the 1st [section]
    '''
    def __init__(self, fpath, line):
        self._f = fpath
        self._l = line
        self._fp = None

    def opts(self):
        self._fp = self._f.fp()
        opts = ConfigParser.SafeConfigParser()
        opts.readfp(self, str(self._f))
        return opts

    def readline(self):
        if self._l:
            l = self._l
            self._l = None
            return l
        else:
            return self._fp.readline()


class Path(object):
    def __init__(self, dirpath, segment=None):
        self._dp = dirpath
        self._seg = segment

    def __str__(self, segment=None):
        if segment is None:
            segment = self._seg
        return path.join(self._dp, seg_ck(segment))


def seg_ck(fn):
    assert path.sep not in fn
    assert path.pathsep not in fn
    return fn


class Dir(Path):
    def subdir(self, segment):
        return Dir(path.join(self._dp, segment))

    def file(self, fn, ext):
        return File(self._dp, fn, ext)


class File(Path):
    def fp(self):
        return open(str(self))

    def exists(self):
        return path.exists(str(self))


def run_report(start_response, opts, section='_database'):
    conn = xataface_connection(opts, section)
    cursor = conn.cursor()
    cursor.execute(QUERY)
    for row in cursor.fetchall():
        print "@@", row


def xataface_connection(opts, section):
    def opt(n):
        v = opts.get(section, n)
        return v[1:-1]  # strip ""s

    return MySQLdb.connect(host=opt('host'), user=opt('user'),
                           passwd=opt('password'), db=opt('name'))
    

QUERY='''
select v.claim_uid
     , co.name, co.address, co.city_st_zip
     , ins.payer_type, ins.id_number
     , c.name as patient_name, c.DOB as patient_dob, ins.patient_sex
     , ins.insured_name, ins.insured_dob, ins.insured_sex
     , ins.patient_address, ins.patient_city, ins.patient_state, ins.patient_zip
     , ins.patient_acode, ins.patient_phone
     , ins.patient_rel
     , ins.insured_address, ins.insured_city, ins.insured_state, ins.insured_zip
     , ins.insured_acode, ins.insured_phone
     , ins.patient_status, ins.patient_status2
     , ins.insured_policy
     , ins.dx1, ins.dx2
     , ins.approval
     , s.session_date
     , '11' as place_of_service
     , 1 as diagnosis_pointer
     , v.cpt as cpt_code
     , v.charge
     , 1 as units
     , v.client_paid
     , concat(upper(substr(c.name, 1, 3)), '.',
              upper(substr(c.name, instr(c.name, ',') + 2, 3)), '.',
              convert(c.id, char)) as patient_account
     , bp.npi
     , bp.tax_id
     , bp.name as provider_name
     , bp.acode as provider_acode
     , bp.phone as provider_phone
     , bp.address as provider_address
     , bp.city_st_zip as provider_city_st_zip
     , char(12) as page_break
from Insurance ins
join Client c on ins.Client_id = c.id
join Carrier co on ins.Carrier_id = co.id
join Visit v on v.Client_id = c.id
join `Session` s on v.Session_id = s.id
join `Group` g on s.Group_id = g.id
join Therapist as bp on bp.tax_id is not null
where v.bill_date is null and v.check_date is null
and v.cpt is not null
and v.claim_uid is not null
order by c.name, v.claim_uid, s.session_date
'''

if __name__ == '__main__':
    if 'SCRIPT_NAME' in environ:
        cgi_main()
    else:
        _test_main()
