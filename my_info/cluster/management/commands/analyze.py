from __future__ import unicode_literals, print_function
import gspread
from django.core.management import BaseCommand
from my_info.cluster.clusterify.affinitypropagationclusterify import \
    AffinityPropagationClusterify


class StreamMixin(object):
    def annotate(self):
        print("MUAHAHA")
        return


class StreamAffinityPropagationClusterify(StreamMixin, AffinityPropagationClusterify):
    pass


class StreamReader(object):
    def __init__(self, topic_list):
        pass


class Command(BaseCommand):
    USERNAME = 'gufougolino@gmail.com'
    PASSWORD = 'ugopassword'
    DOC_TITLE = "clusterify-dataset"

    def handle(self, *args, **options):
        try:
            google_spread = gspread.login(self.USERNAME, self.PASSWORD)
        except gspread.AuthenticationError:
            print("Failed to login with {}".format(self.USERNAME))
            return

        doc = google_spread.open(self.DOC_TITLE)
        clusterify = StreamAffinityPropagationClusterify(StreamReader([]), 4)

        for worksheet in doc.worksheets():
            headers = None
            for line in worksheet.get_all_values():
                if not headers:
                    headers = [x.lower() for x in line]
                    continue
                data = dict(zip(headers, line))

                print(data)

