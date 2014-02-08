import requests


class InterWikiRecon(object):
    def __init__(self):
        pass

    @staticmethod
    def get_inter_wikilinks(page):
        url_recon = 'http://interwikirecon.spaziodati.eu/reconcile?queries={' \
                    '"q0":{"query": "' + page + '"}}'

        results = requests.get(url_recon).json()['q0']['result']

        response = {}
        for result in results:
            if 'EN' in result['type'][0]['name']:
                response['en'] = result['id']
            elif 'IT' in result['type'][0]['name']:
                response['it'] = result['id']

        return response