from __future__ import unicode_literals, print_function
from collections import defaultdict
import gspread
from django.core.management import BaseCommand
from prettytable import PrettyTable
from sklearn.metrics import adjusted_rand_score
from my_info.cluster.clusterify.affinitypropagationclusterify import \
    AffinityPropagationClusterify
from my_info.cluster.clusterify.kmeansclusterify import KMeansClusterify
from my_info.cluster.clusterify.spectralclusterify import SpectralClusterify


class StreamMixin(object):
    def annotate(self):
        self.snippets = self.reader.snippets
        return


class StreamAffinityPropagationClusterify(
        StreamMixin, AffinityPropagationClusterify
):
    pass


class StreamKMeansClusterify(StreamMixin, KMeansClusterify):
    pass


class StreamSpectralClusterify(StreamMixin, SpectralClusterify):
    pass


class StreamReader(object):
    def __init__(self, topic_list):
        self.snippets = {
            idx: dict(annotations={topic: 1})
            for idx, topic in enumerate(topic_list)
        }


class Command(BaseCommand):
    USERNAME = 'gufougolino@gmail.com'
    PASSWORD = 'ugopassword'
    DOC_TITLE = "clusterify-dataset"
    CLUSTER_KLASSES = [StreamAffinityPropagationClusterify,
                       StreamKMeansClusterify,
                       StreamSpectralClusterify]

    def handle(self, *args, **options):
        try:
            google_spread = gspread.login(self.USERNAME, self.PASSWORD)
        except gspread.AuthenticationError:
            print("Failed to login with {}".format(self.USERNAME))
            return

        doc = google_spread.open(self.DOC_TITLE)
        table = PrettyTable([""] + [k.__name__ for k in self.CLUSTER_KLASSES])
        for worksheet in doc.worksheets():
            headers = None
            expected = dict()
            for line in worksheet.get_all_values():
                if not headers:
                    headers = [x.lower() for x in line]
                    continue
                data = dict(zip(headers, line))

                if 'cluster' in data:
                    try:
                        expected[data['entities']] = int(data['cluster'])
                    except ValueError:
                        pass

            topic_sorted = sorted(expected.keys())
            expected_list = [expected[key] for key in topic_sorted]

            k = len(set(expected_list))
            reader = StreamReader(topic_sorted)
            results = []
            for klass in self.CLUSTER_KLASSES:
                clusterify = klass(reader, k)
                clusterify.annotate()
                actual_clusters = clusterify.do_cluster()

                actual = {
                    y: idx
                    for idx, cluster in enumerate(actual_clusters['clusters'])
                    for y in cluster.keys()
                }
                actual_list = [actual[key] for key in topic_sorted]
                results.append(adjusted_rand_score(expected_list, actual_list))
            table.add_row([worksheet.title] + results)

        print(table)
