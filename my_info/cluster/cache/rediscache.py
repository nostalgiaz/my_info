import json
from redis import Redis


class RedisCache(object):
    def __init__(self):
        self.red = Redis()

    def has(self, key):
        return self.red.exists(key)

    def set(self, key, value):
        self.red.set(key, json.dumps(value))
        return value

    def get(self, key):
        return json.loads(self.red.get(key))

    def cleanup(self):
        return self.red.flushdb()
