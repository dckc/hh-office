'''hhtcb -- Hope harbor xataface, WSGI utilities.

hhtcb is now a misnomer, but oh well.
'''

from cgi import parse_qs
from ConfigParser import SafeConfigParser

import ocap


class Xataface(object):
    r'''
    >>> here = ocap.Rd('/here', MockXF, MockXF.open_rd)
    >>> xf = Xataface.make(here)
    >>> def superpower():
    ...     return xf.dbopts()
    >>> ck = xf.mk_qs_facet(superpower)

    >>> opts = ck({'QUERY_STRING': 'key=sekret'})
    >>> opts
    ['localhost', 'mickey_mouse', 'club', 'all_my_friends']

    >>> ck({'QUERY_STRING': ''})
    Traceback (most recent call last):
      ...
    KeyError: 'missing key parameter'

    >>> ck({'QUERY_STRING': 'key=secret'})
    Traceback (most recent call last):
      ...
    IOError: report key does not match.
    '''
    ocap  # pyflakes doesn't see into docstrings

    def __init__(self, configRd):
        self._rd = configRd

    @classmethod
    def make(cls, here,
             ini='conf.ini'):
        return cls(here.subRd(ini))

    DB_SECTION = '_database'

    def mk_qs_facet(self, doit,
                    key_param='key',
                    opt='report_key'):
        def invoke(env):
            k = WSGI.param(env, key_param)

            if self.config().get(self.DB_SECTION, opt) not in k:
                raise IOError('report key does not match.')

            return doit()

        return invoke

    def dbopts(self,
               keys=['host', 'user', 'password', 'name']):
        config = self.config()
        return [config.get(Xataface.DB_SECTION, k)[1:-1]
                for k in keys]

    def webapp_login(self, env):
        return self.mk_qs_facet(doit=lambda: self.dbopts())()

    def config(self,
               pfx='[DEFAULT]'):
        '''
        TODO: factor out of print_report.py
        '''
        config = SafeConfigParser()
        config.readfp(Prefix(self._rd.fp(), pfx), str(self._rd))
        return config


class MockXF(object):
    import pkg_resources as pkg

    # TODO: refactor content as instance var
    content = {'/here/conf.ini':
               '\n'.join([line.strip()
                          for line in '''
               title=before first section

               [_database]
               report_key=sekret
               host="localhost"
               user="mickey_mouse"
               password="club"
               name="all_my_friends"
                          '''.split('\n')]),
               '/here/templates/weekly_groups.html':
               pkg.resource_string(__name__, 'templates/weekly_groups.html')}

    @classmethod
    def open_rd(cls, n):
        from StringIO import StringIO
        return StringIO(cls.content[n])

    @classmethod
    def abspath(cls, p):
        import posixpath
        return posixpath.abspath(p)

    @classmethod
    def join(cls, *paths):
        import posixpath
        return posixpath.join(*paths)

    @classmethod
    def exists(cls, path):
        return path in cls.content


class WSGI:
    PLAIN = [('Content-Type', 'text/plain')]
    HTML8 = [('Content-Type', 'text/html; charset=utf-8')]
    PDF = [('Content-Type', 'application/pdf')]

    QS = 'QUERY_STRING'

    @classmethod
    def param(cls, env, n):
        v = parse_qs(env.get(cls.QS, n)).get(n)
        if not v:
            raise KeyError('missing %s parameter' % n)
        return v

    @classmethod
    def error_middleware(cls, format_exc, app):
        '''
        TODO: factor out of print_report.py
        '''
        def err_app(env, start_response):
            try:
                return app(env, start_response)
            except:  # pylint: disable-msg=W0703,W0702
                start_response('500 internal error', WSGI.PLAIN)
                return [format_exc()]

        return err_app


class Prefix(object):
    '''work-around: xataface needs options before the 1st [section]
    TODO: factor out of print_report.py
    '''
    def __init__(self, fp, line):
        self._fp = fp
        self._l = line

    def readline(self):
        if self._l:
            l = self._l
            self._l = None
            return l
        else:
            return self._fp.readline()
