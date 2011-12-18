#!/usr/bin/env python
import wsgiref.handlers
import cgi

from sqlalchemy import create_engine, exc 
from sqlalchemy.engine.url import URL

import hhtcb
from ocap import DBOpts
from claims.import_claims import Claim

PLAIN = [('Content-Type', 'text/plain')]
HTML8 = [('Content-Type', 'text/html; charset=utf-8')]


def cgi_main():
    wsgiref.handlers.CGIHandler().run(upload_if_key)


def upload_if_key(env, start_response,
                  driver='mysql+mysqldb'):
    dbo = DBOpts(hhtcb.xataface_config())
    try:
        h, u, p, n = dbo.webapp_login(env)
    except KeyError:
        start_response('400 bad request', PLAIN)
        return ['missing key parameter ']
    except OSError:
        start_response('401 unauthorized', PLAIN)
        return ['report key does not match.']

    if env['REQUEST_METHOD'] == 'POST':
        return upload_insurance(env, start_response,
                                create_engine(URL(driver, u, p,
                                                  host=h, database=n)))
    else:
        start_response('200 OK', HTML8)
        return ['<!DOCTYPE html>',
                '<html><head>',
                '<title>Upload Insurance Info - Hope Harbor</title>',
                '</head><body>',
                '<form method="POST" enctype="multipart/form-data">',
                '<p>Choose medclaim file: '
                '<input type="file" name="claim-xls" />',
                '<input type="submit" />',
                '</p></form></body></html>']



def upload_insurance(env, start_response, engine):
    fv = cgi.FieldStorage(fp=env['wsgi.input'], environ=env)

    def bad_request(txts):
        start_response('400 bad request', PLAIN)
        return txts

    if 'claim-xls' not in fv:
        return bad_request(['Missing claim-xls parameter.'])

    c = Claim.from_contents(fv['claim-xls'].file.read())
    try:
        policy = c.load(engine)
    except KeyError as ex:
        return bad_request(['no such client: ', str(ex)])
    except ReferenceError as ex:
        start_response('409 conflict', PLAIN)
        return ['insurance already recorded: ',
                c.patient_name().encode('utf-8')]
    except (exc.IntegrityError, exc.OperationalError) as ex:
        return bad_request(['insert failed: ', str(ex)])

    start_response('201 created', HTML8)
    return ['<p>OK. insurance record created for: ',
            '<a href="index.php?-table=Client&-action=browse&',
            '-recordid=Client%3Fid%3D', str(policy.client.id), '">',
            c.patient_name().encode('utf-8'), '</a></p>']


if __name__ == '__main__':
    from os import environ
    if 'SCRIPT_NAME' in environ:
        cgi_main()
