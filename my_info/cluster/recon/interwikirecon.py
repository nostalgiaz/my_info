import requests
from my_info.cluster.cache import RedisCache


class InterWikiRecon(object):
    def __init__(self):
        self.cache = RedisCache()

    def get_inter_wikilinks(self, page):
        key = "{}:interwikirecon".format(page)
        if not self.cache.has(key):
            url = 'http://interwikirecon.spaziodati.eu/reconcile?queries={' \
                  '"q0":{"query": "' + page + '", "type": "Wikipedia %s"}}'

            try:
                en = requests.get(
                    url.replace("%s", 'EN')).json()['q0']['result'][0]['id']
            except IndexError:
                en = None

            try:
                it = requests.get(
                    url.replace("%s", 'IT')).json()['q0']['result'][0]['id']
            except IndexError:
                it = None

            self.cache.set(key, {
                'en': en,
                'it': it,
            })

        return self.cache.get(key)