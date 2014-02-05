#!/usr/bin/env python
''' export_claims -- export claims in CSV format

https://sfreeclaims.anvicare.com/docs/forms/Reference-CSV%20Specifications.txt
'''

import csv
from itertools import groupby
from operator import itemgetter
import wsgiref.handlers

import MySQLdb

import ocap
from hhtcb import Xataface, WSGI


def cgi_main(xf, cal):
    app = ReportApp(xf, cal)
    wsgiref.handlers.CGIHandler().run(app)


def _test_main(argv, xf):
    outfn, visits = argv[1], argv[2:]
    host, user, password, name = xf.dbopts()

    content, pages = format_claims(MySQLdb.connect(host=host, user=user,
                                                   passwd=password, db=name),
                                   map(int, visits))
    outfp = open(outfn, 'w')
    for part in content:
        outfp.write(part)
    print pages


class ReportApp(object):
    def __init__(self, xf, cal):
        self._xf = xf
        self._datesrc = cal

    def __call__(self, env, start_response):
        try:
            host, user, password, name = self._xf.webapp_login(env)
        except KeyError:
            start_response('400 bad request', WSGI.PLAIN)
            return ['missing key parameter ']
        except OSError:
            start_response('401 unauthorized', WSGI.PLAIN)
            return ['report key does not match.']

        conn = MySQLdb.connect(host=host, user=user, passwd=password, db=name)

        start_response('200 ok',
                       [('content-type', 'text/plain'),
                        ('Content-Disposition',
                         'attachment; filename=claims-%s.csv'
                         % self._datesrc.today())])

        content, pages = format_claims(conn)
        return content


def format_claims(conn, visit_ids):
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(QUERY % dict(
        visit_ids=', '.join([str(i) for i in visit_ids])))

    pages = []
    buf = ListWriter()
    out = csv.DictWriter(buf, COLUMNS, quoting=csv.QUOTE_ALL)
    out.writerow(dict(zip(COLUMNS, COLUMNS)))

    for client_id, records in by_page(groupby(cursor.fetchall(),
                                              itemgetter('client_id')),
                                      pg_size=6):
        claim = records[0]

        tot = claim['28-TotalCharge']
        for idx in range(1, len(records)):
            for k, v in records[idx].items():
                if k.startswith('24.'):
                    kk = k.replace('.1.', '.%d.' % (idx + 1))
                    claim[kk] = v
                if k == '24.1.f-Charges':
                    tot += v

        claim['28-TotalCharge'] = tot
        # is there ever an amount paid?
        claim['30-BalanceDue'] = tot

        #import pprint
        #pprint.pprint(claim)
        visit_ids = [r['visit_id'] for r in records]
        pages.append(dict(client_id=client_id,
                          total=tot,
                          visit_ids=visit_ids,
                          items=records,
                          detail=claim))
        del claim['client_id']
        del claim['visit_id']
        out.writerow(claim)

    return buf.parts, pages


def by_page(record_groups, pg_size):
    for k, group in record_groups:
        gl = list(group)
        offset = 0
        while offset < len(gl):
            yield k, gl[offset:offset + pg_size]
            offset += pg_size


class ListWriter(object):
    def __init__(self):
        self.parts = []

    def write(self, txt):
        self.parts.append(txt)


QUERY = r'''
select c.id client_id, v.id visit_id
     , co.name as `Insurance Company Name`
     , co.address `Insurance Company Address 1`
     , co.city_st_zip `Insurance Company Address 2`
     , ins.payer_type `1-InsuredPlanName`
     , ins.id_number `1a-InsuredIDNo`
     , c.name as `2-PatientName`
     , date_format(c.DOB, '%%m/%%d/%%Y') as `3-PatientDOB`
     , ins.patient_sex `3-PatientGender`
     , case when upper(ins.patient_rel) = 'SELF'
       then c.name
       else ins.insured_name end `4-InsuredName`
     , c.address `5-PatientAddress`
     , c.city `5-PatientCity`
     , c.state `5-PatientState`
     , c.zip `5-PatientZip`
     , c.phone `5-PatientPhone`
     , upper(ins.patient_rel) `6-PatientRel`
     , case when upper(ins.patient_rel) = 'SELF'
       then c.address
       else ins.insured_address end `7-InsuredAddr`
     , case when upper(ins.patient_rel) = 'SELF'
       then c.city
       else ins.insured_city end `7-InsAddCity`
     , case when upper(ins.patient_rel) = 'SELF'
       then c.state
       else ins.insured_state end `7-InsAddState`
     , case when upper(ins.patient_rel) = 'SELF'
       then c.zip
       else ins.insured_zip end `7-InsAddZip`
     , case when upper(ins.patient_rel) = 'SELF'
       then c.phone
       else ins.insured_phone end `7-InsAddPhone`
     , ins.patient_status `8-MaritalStatus`
     , ins.patient_status2 `8-Employed?`
     , 'NO' as `10a-CondEmployment`
     , 'NO' as `10b-CondAutoAccident`
     , 'NO' as `10c-CondOtherAccident`
     , ins.insured_policy `11-InsuredGroupNo`
     , date_format(case when upper(ins.patient_rel) = 'SELF'
                   then c.dob
                   else ins.insured_dob end, '%%m/%%d/%%Y') `11a-InsuredsDOB`
     , case when upper(ins.patient_rel) = 'SELF'
       then ins.patient_sex
       else ins.insured_sex end `11a-InsuredsGender`
     , 'Signature on file' `12-PatientSign`
     , date_format(current_date, '%%m/%%d/%%Y') `12-Date`
     , 'Signature on file' as `13-AuthSign`
     , 'NO' as `20-OutsideLab`
     , '0.00' as `20-Charges`
     , ins.dx1 `21.1-Diagnosis`
     , ins.dx2 `21.2-Diagnosis`
     , ins.approval `23-PriorAuth`

     , date_format(s.session_date, '%%m/%%d/%%Y') `24.1.a-DOSFrom`
     , date_format(s.session_date, '%%m/%%d/%%Y') `24.1.a-DOSTo`
     , v.cpt as `24.1.d-CPT`
     , '11' as `24.1.b-Place`
     , 1 as `24.1.e-Code`
     , p.price `24.1.f-Charges`
     , 1 as `24.1.g-Units`
     , bp.npi `24.1.j-ProvNPI`

     , bp.tax_id `25-TaxID`
     , 'SSN' as `25-SSN/EIN`
     , concat(upper(substr(c.name, 1, 3)), '.',
              upper(substr(c.name, instr(c.name, ',') + 2, 3)), '.',
              convert(c.id, char)) as `26-PatientAcctNo`
     , 'Y' as `27-AcceptAssign`
     , p.price as `28-TotalCharge`
     , 0 `29-AmountPaid`
     , p.price as `30-BalanceDue`
     , bp.name as `31-PhysicianSignature`
     , date_format(current_date, '%%m/%%d/%%Y') `31-Date`
     , bp.name `33-ClinicName`
     , bp.address as `33-ClinicAddressLine1`
     , bp.city_st_zip as `33-ClinicCityStateZip`
     , bp.npi as `33-a-NPI`
from Insurance ins
join Client c on ins.Client_id = c.id
join Carrier co on ins.Carrier_id = co.id
join Visit v on v.Client_id = c.id
join `Procedure` p on p.cpt = v.cpt
join `Session` s on v.Session_id = s.id
join `Group` g on s.Group_id = g.id
join Therapist as bp on bp.tax_id is not null
where v.bill_date is null and v.check_date is null
and v.id in (%(visit_ids)s)
order by c.name, c.id, s.session_date, v.id
'''

COLUMNS = [literal.strip()[1:-1] for literal in '''
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
    def _with_caps():
        from os import environ, path as os_path
        import datetime

        here = ocap.Rd(os_path.dirname(__file__), os_path,
                       open_rd=lambda n: open(n))
        xf = Xataface.make(here)

        if 'SCRIPT_NAME' in environ:
            cgi_main(xf, cal=datetime.date)
        else:
            from sys import argv
            _test_main(argv, xf)
