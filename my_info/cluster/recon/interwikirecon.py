import requests
from my_info.cluster.cache import RedisCache


class InterWikiRecon(object):
    def __init__(self):
        self.cache = RedisCache()
        self.requests = requests.session()

    def get_inter_wikilinks(self, page):
        """
        >>> a = InterWikiRecon()
        >>> a.get_inter_wikilinks('http://it.wikipedia.org/wiki/Mozilla')
        {u'EN': u'http://en.wikipedia.org/wiki/Mozilla', \
u'IT': u'http://it.wikipedia.org/wiki/Mozilla'}
        >>> a.get_inter_wikilinks('http://en.wikipedia.org/wiki/Mozilla')
        {u'EN': u'http://en.wikipedia.org/wiki/Mozilla', \
u'IT': u'http://it.wikipedia.org/wiki/Mozilla'}
        """
        key = "{}:interwikirecon".format(page)
        if not self.cache.has(key):

            given_lang = 'IT' if '://it.' in page else 'EN'
            new_lang = 'IT' if given_lang == 'EN' else 'EN'

            url = 'http://interwikirecon.spaziodati.eu/reconcile?' \
                  'queries={"q0":{"query": "%s", "type": "Wikipedia %s"}}' \
                  '' % (page, new_lang)

            try:
                new_page = self.requests.get(url).json()['q0']['result'][0]['id']
            except IndexError:
                new_page = None

            self.cache.set(key, {
                given_lang: page,
                new_lang: new_page,
            })

        return self.cache.get(key)
