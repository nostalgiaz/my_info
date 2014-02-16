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
        if not self.cache.has(self.cache_key) or DEBUG_CACHE:
            annotated_texts_tmp = [
                self.datatxt.nex(text) for text in self.texts
            ]
            annotated_texts = {
                x['id']: x for x in annotated_texts_tmp if x is not None
            }

            for k, v in annotated_texts.iteritems():
                del v['id']

            if DEBUG_CACHE:
                return annotated_texts

            return self.cache.set(self.cache_key, annotated_texts)

        return self.cache.get(self.cache_key)
