from hashlib import sha1
from celery.utils.log import get_task_logger
from dandelion import datatxt, DandelionException
from my_info.cluster.cache import RedisCache
from my_info.cluster.recon.interwikirecon import InterWikiRecon
from my_info.settings import DATATXT_APP_ID, DATATXT_APP_KEY
import requests

logger = get_task_logger(__name__)


class DataTXT(object):
    def __init__(self):
        self.interWikiRecon = InterWikiRecon()
        self.cache = RedisCache()
        self.datatxt = datatxt.DataTXT(
            app_id=DATATXT_APP_ID,
            app_key=DATATXT_APP_KEY,
        )

    def nex(self, *args):
        try:
            annotated = self.datatxt.nex(
                args[0],
                min_confidence=.7,
                parse_hashtag=True,
            )
            id = sha1(annotated.lang + str(annotated.annotations)).hexdigest()

            return {
                'id': id,
                'lang': annotated.lang,
                'annotations': {
                    a.uri: a for a in annotated.annotations
                }
            }
        except DandelionException:
            logger.info("dandelion exception")

    @staticmethod
    def _rel_request(lang, topic1, topic2):
        url = 'http://localhost:18080/datatxt/relatedness'
        try:
            return requests.get(url, params={
                'lang': lang,
                'page1': topic1,
                'page2': topic2,
            }).json()['relatedness']
        except Exception:  # topic1 or topic2 doesn't exist
            return 0

    def rel(self, topic1, topic2, enable_cache=True):
        topics = sorted([topic1, topic2])
        topic1, topic2 = topics[0], topics[1]
        cache_key = "{}-{}:relatedness".format(topic1, topic2)

        lang1 = 'it' if '://it.' in topic1 else 'en'
        lang2 = 'it' if '://it.' in topic2 else 'en'

        if enable_cache and not self.cache.has(cache_key):
            if lang1 == lang2:
                value = self._rel_request(lang1, topic1, topic2)
            else:
                topic1_pages = self.interWikiRecon.get_inter_wikilinks(topic1)
                topic2_pages = self.interWikiRecon.get_inter_wikilinks(topic2)

                topic1_en = topic1_pages.get('en')
                topic1_it = topic1_pages.get('it')
                topic2_en = topic2_pages.get('en')
                topic2_it = topic2_pages.get('it')
                value_en = -1
                value_it = -1

                if topic1_en is not None and topic2_en is not None:
                    value_en = self._rel_request('en', topic1_en, topic2_en)

                if topic1_it is not None and topic2_it is not None:
                    value_it = self._rel_request('it', topic1_it, topic2_it)

                if value_it != -1 and value_en != -1:
                    value = (value_en + value_it) / 2.
                elif value_it == -1 and value_en != -1:
                    value = value_en
                elif value_it != -1 and value_en == -1:
                    value = value_it
                else:
                    value = 0

            self.cache.set(cache_key, value)

        return self.cache.get(cache_key)
