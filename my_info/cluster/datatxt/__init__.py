from hashlib import sha1
from celery.utils.log import get_task_logger
from dandelion import datatxt, DandelionException
from numpy import zeros
from my_info.cluster.cache import RedisCache
from my_info.cluster.recon.interwikirecon import InterWikiRecon
from my_info.settings import DATATXT_APP_ID, DATATXT_APP_KEY
import requests

logger = get_task_logger(__name__)


class DataTXT(object):
    def __init__(self):
        self.interWikiRecon = InterWikiRecon()
        self.cache = RedisCache()
        self.requests = requests.session()
        self.datatxt = datatxt.DataTXT(
            app_id=DATATXT_APP_ID,
            app_key=DATATXT_APP_KEY,
        )

    def nex(self, *args):
        try:
            annotated = self.datatxt.nex(
                args[0],
                min_confidence=.6,
                parse_hashtag=True,
                epsilon=.5,
            )
            id_ = sha1(annotated.lang + str(annotated.annotations)).hexdigest()

            return {
                'id': id_,
                'lang': annotated.lang,
                'annotations': {
                    a.uri: a for a in annotated.annotations
                }
            }
        except DandelionException:
            logger.info("dandelion exception: " + args[0])

    def _rel_request(self, lang, topic1, topic2):
        if all(x is None for x in topic1) or all(x is None for x in topic2):
            return {}

        url = 'http://api.dandelion.eu/datatxt/rel/v1'
        response = self.requests.get(url, params={
            'lang': lang,
            'topic1': topic1,
            'topic2': topic2,
            '$app_id': DATATXT_APP_ID,
            '$app_key': DATATXT_APP_KEY,
        })

        if response.ok:
            return response.json()
        print response.json()
        return {}

    def rel(self, topics1, topics2, enable_cache=True):
        rel = zeros((len(topics1), len(topics2)))

        response = None
        for i, topic1 in enumerate(topics1):
            for j, topic2 in enumerate(topics2):
                cache_key = "{}-{}:relatedness".format(topic1, topic2)
                if enable_cache and self.cache.has(cache_key):
                    value = self.cache.get(cache_key)
                else:
                    if response is None:
                        response = self._rel(topics1, topics2)
                    value = response[i][j]
                    self.cache.set(cache_key, value)

                rel[i][j] = value
        return rel

    def _rel(self, topics1, topics2):

        def lang_topic(topics, wanted_lang):
            for topic in topics:
                lang = 'it' if '://it.' in topic else 'en'
                if lang == wanted_lang:
                    yield topic
                else:
                    pages = self.interWikiRecon.get_inter_wikilinks(topic)
                    yield pages.get(wanted_lang.upper())

        it_topics1 = list(lang_topic(topics1, 'it'))
        it_topics2 = list(lang_topic(topics2, 'it'))
        en_topics1 = list(lang_topic(topics1, 'en'))
        en_topics2 = list(lang_topic(topics2, 'en'))

        it_response = {
            tuple(sorted([x['topic1']['topic']['uri'], x['topic2']['topic']['uri']])): x['weight']
            for x in self._rel_request('it', it_topics1, it_topics2).get('relatedness', [])
            if not x.get('error', False)
        }
        en_response = {
            tuple(sorted([x['topic1']['topic']['uri'], x['topic2']['topic']['uri']])): x['weight']
            for x in self._rel_request('en', en_topics1, en_topics2).get('relatedness', [])
            if not x.get('error', False)
        }

        response = zeros((len(topics1), len(topics2)))
        for i, (it_topic1, en_topic1) in enumerate(zip(it_topics1, en_topics1)):
            for j, (it_topic2, en_topic2) in enumerate(zip(it_topics2, en_topics2)):
                value_it = it_response.get(
                    tuple(sorted([it_topic1, it_topic2])), 0.
                )
                value_en = en_response.get(
                    tuple(sorted([en_topic1, en_topic2])), 0.
                )

                response[i][j] = max(value_it, value_en)
        return response
