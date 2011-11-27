''' export_claims -- export claims in CSV format

https://sfreeclaims.anvicare.com/docs/forms/Reference-CSV%20Specifications.txt
'''

from os import path, environ
import ConfigParser
import csv
import itertools

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
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(QUERY)

    start_response('200 ok',
                   (('content-type', 'text/plain'),
                    ('Content-Disposition',
                     'attachment; filename=claims.csv')))

    buf = ListWriter()
    out = csv.DictWriter(buf, COLUMNS,
                         extrasaction='ignore',  #@@ignore
                         quoting=csv.QUOTE_ALL)
    out.writerow(dict(zip(COLUMNS, COLUMNS)))
    
    for claim_uid, records in itertools.groupby(cursor.fetchall(),
                                                lambda r: r['claim_uid']):
        ## TODO: output headers
        ## TODO: quote all values
        ## TODO: grouping
        ## TODO: formatting of dates, None/null
        claim = list(records)[0]
        out.writerow(claim)

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
    

QUERY=r'''
select v.claim_uid
     , co.name as `Insurance Company Name`
     , co.address `Insurance Company Address 1`
     , co.city_st_zip `Insurance Company Address 2`
     , ins.payer_type `1-InsuredPlanName`
     , ins.id_number `1a-InsuredIDNo`
     , c.name as `2-PatientName`
     , date_format(c.DOB, '%m/%d/%Y') as `3-PatientDOB`
     , ins.patient_sex `3-PatientGender`
     , ins.insured_name `4-InsuredName`
     , ins.patient_address `5-PatientAddress`
     , ins.patient_city `5-PatientCity`
     , ins.patient_state `5-PatientState`
     , ins.patient_zip `5-PatientZip`
     , concat(ins.patient_acode, '-', ins.patient_phone) `5-PatientPhone`
     , upper(ins.patient_rel) `6-PatientRel`
     , ins.insured_address `7-InsuredAddr`
     , ins.insured_city `7-InsAddCity`
     , ins.insured_state `7-InsAddState`
     , ins.insured_zip `7-InsAddZip`
     , concat(ins.insured_acode, '-', ins.insured_phone) `7-InsAddPhone`
     , ins.patient_status `8-MaritalStatus`
     , ins.patient_status2 `8-Employed?`
     , 'NO' as `10a-CondEmployment`
     , 'NO' as `10b-CondAutoAccident`
     , 'NO' as `10c-CondOtherAccident`
     , ins.insured_policy `11-InsuredGroupNo`
     , date_format(ins.insured_dob, '%m/%d/%Y') `11a-InsuredsDOB`
     , ins.insured_sex `11a-InsuredsGender`
     , 'Signature on file' `12-PatientSign`
     , date_format(current_date, '%m/%d/%Y') `12-Date`
     , 'Signature on file' as `13-AuthSign`
     , 'NO' as `20-OutsideLab`
     , '0.00' as `20-Charges`
     , ins.dx1 `21.1-Diagnosis`
     , ins.dx2 `21.2-Diagnosis`
     , ins.approval `23-PriorAuth`

     , date_format(s.session_date, '%m/%d/%Y') `24.1.a-DOSFrom`
     , date_format(s.session_date, '%m/%d/%Y') `24.1.a-DOSTo`
     , v.cpt as `24.1.d-CPT`
     , '11' as `24.1.b-Place`
     , 1 as `24.1.e-Code`
     , v.charge `24.1.f-Charges`
     , 1 as `24.1.g-Units`
     , bp.npi `24.1.j-ProvNPI`

     , bp.tax_id `25-TaxID`
     , 'SSN' as `25-SSN/EIN`
     , concat(upper(substr(c.name, 1, 3)), '.',
              upper(substr(c.name, instr(c.name, ',') + 2, 3)), '.',
              convert(c.id, char)) as `26-PatientAcctNo`
     , 'YES' as `27-AcceptAssign`
     , v.charge as `28-TotalCharge` -- @@TODO
     , 0 -- @@???
     , v.charge as `30-BalanceDue` -- @@???
     , bp.name as `31-PhysicianSignature`
     , date_format(current_date, '%m/%d/%Y') `31-Date`
     , bp.name `33-ClinicName`
     , bp.address as `33-ClinicAddressLine1`
     , bp.city_st_zip as `33-ClinicCityStateZip`
     , bp.npi as `33-a-NPI`
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
