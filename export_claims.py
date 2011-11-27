''' export_claims -- export claims in CSV format

https://sfreeclaims.anvicare.com/docs/forms/Reference-CSV%20Specifications.txt
'''

from os import path, environ
import ConfigParser
import csv

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
    cursor = conn.cursor()  #.cursor(MySQLdb.cursors.DictCursor)?
    cursor.execute(QUERY)

    start_response('200 ok',
                   (('content-type', 'text/plain'),
                    ('Content-Disposition',
                     'attachment; filename=claims.csv')))

    buf = ListWriter()
    out = csv.DictWriter(buf, COLUMNS)
    out.writerow(dict(zip(COLUMNS, COLUMNS)))
    
    for row in cursor.fetchall():
        ## TODO: output headers
        ## TODO: quote all values
        ## TODO: grouping
        ## TODO: formatting of dates, None/null
        out.writerow(dict(zip(COLUMNS, [str(v) for v in row])))

    return buf.parts


class ListWriter(object):
    def __init__(self):
        self.parts = []

    def write(self, txt):
        self.parts.append(txt)


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

COLUMNS=[literal.strip()[1:-1] for literal in '''
            "Insurance Company Name"
            "Insurance Company Name 2"
            "Insurance Company Address 1"
            "Insurance Company Address 2"

             "1-InsuredPlanName"
             "1a-InsuredIDNo"
             "2-PatientName"
             "3-PatientDOB"
             "3-PatientGender"
             "4-InsuredName"
             "5-PatientAddress"
             "5-PatientCity"
             "5-PatientState"
             "5-PatientZip"
             "5-PatientPhone"
             "6-PatientRel"
             "7-InsuredAddr"
             "7-InsAddCity"
             "7-InsAddState"
             "7-InsAddZip"
             "7-InsAddPhone"
             "8-MaritalStatus"
             "8-Employed?"
             "9-InsuredName2"
             "9a-InsuredGroupNo2"
             "9b-Insureds2DOB"
             "9b-Insureds2Gender"
             "9c-EmployerName"
             "9d-InsuredPlanName2"
             "10a-CondEmployment"
             "10b-CondAutoAccident"
             "10c-CondOtherAccident"
             "10b2-AccidentState"
             "10d-LocalUse"
             "11-InsuredGroupNo"
             "11a-InsuredsDOB"
             "11a-InsuredsGender"
             "11b-EmployerName"
             "11c-InsuredPlanName"
             "11d-OtherHealthPlan"
             "12-PatientSign"
             "12-Date"
             "13-AuthSign"
             "14-DateOfCondition"
             "15-FirstDateOfCondition"
             "16-DateFromNoWork"
             "16-DateToNoWork"
             "17-ReferringPhysician"
             "17a-PhysicianNo"
             "17b-ReferNPI"
             "18-DateFromHosp"
             "18-DateToHosp"
             "19-LocalUse"
             "20-OutsideLab"
             "20-Charges"
             "21.1-Diagnosis"
             "21.2-Diagnosis"
             "21.3-Diagnosis"
             "21.4-Diagnosis"
             "22-MedicaidResubmissionCode"
             "22-MedicaidResubmissionRefNo"
             "23-PriorAuth"

             "24.1.a-DOSFrom"
             "24.1.a-DOSTo"
             "24.1.b-Place"
             "24.1.c-EMG"
             "24.1.d-CPT"
             "24.1.d-Modifier"
             "24.1.e-Code"
             "24.1.f-Charges"
             "24.1.g-Units"
             "24.1.h-Epsot"
             "24.1.i-Qualifier"
             "24.1.j-ProvLegacyNo"
             "24.1.j-ProvNPI"
             "24.2.a-DOSFrom"
             "24.2.a-DOSTo"
             "24.2.b-Place"
             "24.2.c-EMG"
             "24.2.d-CPT"
             "24.2.d-Modifier"
             "24.2.e-Code"
             "24.2.f-Charges"
             "24.2.g-Units"
             "24.2.h-Epsot"
             "24.2.i-Qualifier"
             "24.2.j-ProvLegacyNo"
             "24.2.j-ProvNPI"
             "24.3.a-DOSFrom"
             "24.3.a-DOSTo"
             "24.3.b-Place"
             "24.3.c-EMG"
             "24.3.d-CPT"
             "24.3.d-Modifier"
             "24.3.e-Code"
             "24.3.f-Charges"
             "24.3.g-Units"
             "24.3.h-Epsot"
             "24.3.i-Qualifier"
             "24.3.j-ProvLegacyNo"
             "24.3.j-ProvNPI"
             "24.4.a-DOSFrom"
             "24.4.a-DOSTo"
             "24.4.b-Place"
             "24.4.c-EMG"
             "24.4.d-CPT"
             "24.4.d-Modifier"
             "24.4.e-Code"
             "24.4.f-Charges"
             "24.4.g-Units"
             "24.4.h-Epsot"
             "24.4.i-Qualifier"
             "24.4.j-ProvLegacyNo"
             "24.4.j-ProvNPI"
             "24.5.a-DOSFrom"
             "24.5.a-DOSTo"
             "24.5.b-Place"
             "24.5.c-EMG"
             "24.5.d-CPT"
             "24.5.d-Modifier"
             "24.5.e-Code"
             "24.5.f-Charges"
             "24.5.g-Units"
             "24.5.h-Epsot"
             "24.5.i-Qualifier"
             "24.5.j-ProvLegacyNo"
             "24.5.j-ProvNPI"
             "24.6.a-DOSFrom"
             "24.6.a-DOSTo"
             "24.6.b-Place"
             "24.6.c-EMG"
             "24.6.d-CPT"
             "24.6.d-Modifier"
             "24.6.e-Code"
             "24.6.f-Charges"
             "24.6.g-Units"
             "24.6.h-Epsot"
             "24.6.i-Qualifier"
             "24.6.j-ProvLegacyNo"
             "24.6.j-ProvNPI"
             "25-TaxID"
             "25-SSN/EIN"
             "26-PatientAcctNo"
             "27-AcceptAssign"
             "28-TotalCharge"
             "29-AmountPaid"
             "30-BalanceDue"
             "31-PhysicianSignature"
             "31-Date"
             "32-FacilityName"
             "32-FacilityAddressLine1"
             "32-FacilityAddressLine2"
             "32-FacilityCityStateZip"
             "32-FacilityNPI"
             "33-ClinicName"
             "33-ClinicAddressLine1"
             "33-ClinicAddressLine2"
             "33-ClinicCityStateZip"
             "33-PIN#"
             "33-GRP#"
             "33-a-NPI"
             "33-b-GrpLegacyNo"
'''.strip().split('\n')]

if __name__ == '__main__':
    if 'SCRIPT_NAME' in environ:
        cgi_main()
    else:
        _test_main()
