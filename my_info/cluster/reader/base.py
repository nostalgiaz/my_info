"""
Base Reader
"""
from my_info.cluster.cache import RedisCache


class BaseReader(object):
    def __init__(self, **kwargs):
        self.cache_key = "{}:{}".format(self.__class__.__name__, kwargs)
        self.cache = RedisCache()

    def texts(self):
        if not self.cache.has(self.cache_key):
            return self.cache.set(self.cache_key, self._texts())

        return self.cache.get(self.cache_key)

    def _texts(self):
        return []
