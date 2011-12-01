from cgi import parse_qs
import ConfigParser

DB_SECTION = '_database'


def _test_config():
    from StringIO import StringIO
    doc = StringIO('[_database]\n'
                    'report_key=sekret\n'
                    'host="localhost"\n'
                    'user="mickey_mouse"\n'
                    'password="club"\n'
                    'name="all_my_friends"\n')
    opts = ConfigParser.SafeConfigParser()
    opts.readfp(doc)
    return opts


class DBOpts(object):
    r'''
    >>> d = DBOpts(_test_config())
    >>> d.webapp_login({'QUERY_STRING': 'key=sekret'})
    ['localhost', 'mickey_mouse', 'club', 'all_my_friends']

    >>> d.webapp_login({'QUERY_STRING': ''})
    Traceback (most recent call last):
      ...
    KeyError: 'missing key parameter'

    >>> d.webapp_login({'QUERY_STRING': 'key=secret'})
    Traceback (most recent call last):
      ...
    OSError: report key does not match.
    '''
    def __init__(self, config):
        self._config = config

    def webapp_login(self, env):
        k = parse_qs(env.get('QUERY_STRING', '')).get('key')
        if not k:
            raise KeyError('missing key parameter')

        if self._config.get(DB_SECTION, 'report_key') not in k:
            raise OSError('report key does not match.')

        return dbopts(self._config)


def dbopts(config):
    '''
    >>> dbopts(_test_config())
    ['localhost', 'mickey_mouse', 'club', 'all_my_friends']
    '''
    return [config.get(DB_SECTION, k)[1:-1]
            for k in ('host', 'user', 'password', 'name')]


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
