from my_info.cluster.cache import RedisCache
from my_info.cluster.datatxt import DataTXT
from my_info.settings import DEBUG_CACHE


class Annotator(object):
    def __init__(self, texts):
        self.cache_key = "{}:{}:annotator".format(
            self.__class__.__name__,
            texts
        )
        self.texts = texts
        self.cache = RedisCache()
        self.datatxt = DataTXT()

    def annotate(self):
        if DEBUG_CACHE:
            return [self.datatxt.nex(text) for text in self.texts]

        if not self.cache.has(self.cache_key):
            annotated_texts = [self.datatxt.nex(text) for text in self.texts]
            print "*" * 80
            #annotated_text = 'annotated_text'
            return self.cache.set(self.cache_key, annotated_texts)

        print "=" * 80
        return self.cache.get(self.cache_key)
