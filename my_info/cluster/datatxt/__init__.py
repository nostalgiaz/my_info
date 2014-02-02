import hashlib
from dandelion import datatxt, DandelionException
from werkzeug.exceptions import TooManyRequests
from my_info.settings import DATATXT_APP_ID, DATATXT_APP_KEY
import requests


class DataTXT(object):
    def __init__(self):
        self._cache = {}
        self.datatxt = datatxt.DataTXT(
            app_id=DATATXT_APP_ID,
            app_key=DATATXT_APP_KEY,
        )

    def nex(self, *args):
        try:
            annotated = self.datatxt.nex(args[0], lang='en', min_confidence=.6)
            return {
                'id': hashlib.sha1(
                    annotated.lang + str(annotated.annotations)).hexdigest(),
                'lang': annotated.lang,
                'annotations': [ann.uri for ann in annotated.annotations],
                'confidence': [ann.confidence for ann in annotated.annotations]
            }
        except DandelionException:
            return {
                'id': 'undefined',
                'lang': 'undefined',
                'annotations': [],
                'confidence': '0',
            }

    def rel(self, topic1, topic2):
        key = "{}{}".format(topic1, topic2)
        if key not in self._cache:
            value = requests.get(
                'http://localhost:18080/datatxt/relatedness', params={
                    'lang': 'en',
                    'page1': topic1,
                    'page2': topic2,
                }
            ).json()['relatedness']
            self._cache[key] = value

        return self._cache[key]
