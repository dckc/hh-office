class Rd(object):
    def __init__(self, path, os_path, open_rd):
        self._os_path = os_path
        self._open_rd = open_rd
        self._path = os_path.abspath(path)

    def __str__(self, segment=None):
        return self._path

    def subRd(self, n):
        p = self._os_path
        return Rd(p.join(self._path, n), p, self._open_rd)

    def fp(self):
        return self._open_rd(self._path)

    def exists(self):
        return self._os_path.exists(str(self))
