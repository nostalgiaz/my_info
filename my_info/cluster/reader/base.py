"""
Base Reader
"""
from my_info.cluster.cache import RedisCache


class BaseReader(object):
    def __init__(self, **kwargs):
        pass

    def texts(self):
        return self._texts()

    def _texts(self):
        return []
