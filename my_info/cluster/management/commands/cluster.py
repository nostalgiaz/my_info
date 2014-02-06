import pprint

from django.core.management import BaseCommand
from my_info.cluster.clusterify.spectralclusterify import SpectralClusterify
from my_info.cluster.clusterify.kmeansclusterify import KMeansClusterify
from my_info.cluster.clusterify.starclusterify import StarClusterify
from my_info.cluster.reader import TwitterReader


class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args) != 2 or args[1] not in ["star", "spectral", "kmeans"]:
            print "Usage: python manage.py cluster <twitter_username> " \
                  "<star|spectra|kmeans>"
            return

        pp = pprint.PrettyPrinter(indent=4)
        username = args[0]
        reader = TwitterReader(username)

        try:
            clusterify = None

            if args[1] == "spectral":
                clusterify = SpectralClusterify(reader)
            elif args[1] == "star":
                clusterify = StarClusterify(reader)
            elif args[1] == "kmeans":
                clusterify = KMeansClusterify(reader)

            clusterify.annotate()
            pp.pprint(clusterify.do_cluster())
        except:
            import traceback
            traceback.print_exc()
