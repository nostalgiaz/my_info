from my_info.cluster.cache import RedisCache


class Annotator(object):
    def __init__(self, texts):
        self.cache_key = "{}:{}:annotator".format(
            self.__class__.__name__,
            texts
        )
        self.cache = RedisCache()

    def annotate(self):
        if not self.cache.has(self.cache_key):
            print "*" * 80
            annotated_text = 'annotated_text'
            return self.cache.set(self.cache_key, annotated_text)

        print "=" * 80
        return self.cache.get(self.cache_key)
