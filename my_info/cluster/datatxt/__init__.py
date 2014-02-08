from hashlib import sha1
from dandelion import datatxt, DandelionException
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
            id = sha1(annotated.lang + str(annotated.annotations)).hexdigest()

            return {
                'id': id,
                'lang': annotated.lang,
                'text': args[0],
                'annotations': {
                    a.uri: a.confidence for a in annotated.annotations
                }
            }
        except DandelionException:
            pass

    def rel(self, topic1, topic2):
        """
            1) se le dire pagine sono nella stessa lingua, fai quello che stai facendo ora
            2) se sono in due lingue diverse, calcola tramite il recon il topic relativo nelle altre lingue
            2a) se entrambe hanno una pagina anche nell'altra lingua, fai la media delle due relatedness (o anche il max, vedi tu)
            2b) se solo una ha la traduzione, restituisci la relatedness in quella lingua solo
            2c) se nessuna delle due ha la pagina corrispondente (raro, secondo me) restituisci 0
        """
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
