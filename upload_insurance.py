#!/usr/bin/env python

from cgi import FieldStorage
import logging

from sqlalchemy import exc
from sqlalchemy.engine.url import URL

import ocap
from hhtcb import Xataface, WSGI
from claims.import_claims import Claim

log = logging.getLogger(__name__)


def cgi_main(mkCGIHandler, upload_app):
    mkCGIHandler().run(upload_app)


def mk_db_engine(create_engine, xf,
                 driver='mysql+mysqldb',
                 db_section='_database'):
    def db_engine():
        config = xf.config()
        h, u, p, n = [config.get(db_section, k)[1:-1]
                      for k in ['host', 'user', 'password', 'name']]
        log.debug('db opts: %s', [h, u, p, n])
        return create_engine(URL(driver, u, p,
                                 host=h, database=n))
    return db_engine


def mk_upload_app(db_access):
    def handle(env, start_response):
        try:
            engine = db_access(env)
        except KeyError:
            start_response('400 bad request', WSGI.PLAIN)
            return ['missing key parameter ']
        except IOError:
            start_response('401 unauthorized', WSGI.PLAIN)
            return ['report key does not match.']

        if env['REQUEST_METHOD'] == 'POST':
            return upload_insurance(env, start_response, engine)
        else:
            start_response('200 OK', WSGI.HTML8)
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
    fv = FieldStorage(fp=env['wsgi.input'], environ=env)

    def bad_request(txts):
        start_response('400 bad request', WSGI.PLAIN)
        return txts

    if 'claim-xls' not in fv:
        return bad_request(['Missing claim-xls parameter.'])

    c = Claim.from_contents(fv['claim-xls'].file.read())
    try:
        policy = c.load(engine)
    except KeyError as ex:
        return bad_request(['no such client: ', str(ex)])
    except ReferenceError as ex:
        start_response('409 conflict', WSGI.PLAIN)
        return ['insurance already recorded: ',
                c.patient_name().encode('utf-8')]
    except (exc.IntegrityError, exc.OperationalError) as ex:
        return bad_request(['insert failed: ', str(ex)])

    start_response('201 created', WSGI.HTML8)
    return ['<p>OK. insurance record created for: ',
            '<a href="index.php?-table=Client&-action=browse&',
            '-recordid=Client%3Fid%3D', str(policy.client.id), '">',
            c.patient_name().encode('utf-8'), '</a></p>']


if __name__ == '__main__':
    def _with_caps():
        from traceback import format_exc
        from os import environ, path
        from wsgiref.handlers import CGIHandler

        from sqlalchemy import create_engine

        here = ocap.Rd(path.dirname(__file__), path,
                       lambda n: open(n))
        xf = Xataface.make(here)
        db_engine = mk_db_engine(create_engine, xf)
        upload_app = mk_upload_app(db_access=xf.mk_qs_facet(db_engine))

        if 'SCRIPT_NAME' in environ:
            cgi_main(mkCGIHandler=lambda: CGIHandler(),
                     upload_app=WSGI.error_middleware(format_exc, upload_app))

    _with_caps()
