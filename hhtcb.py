from os import path

import libxml2

from ocap import PrefixConfig


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

    def file(self, fn):
        return File(self._dp, fn)


class File(Path):
    def fp(self):
        return open(str(self))

    def xml_content(self):
        return libxml2.parseFile(str(self))

    def exists(self):
        return path.exists(str(self))


def xataface_config(ini='conf.ini'):
    here = path.dirname(__file__)
    return PrefixConfig(File(here, ini), '[DEFAULT]').opts()
