from django.core.management import BaseCommand

from my_info.cluster.clusterify import SpectralClusterify
from my_info.cluster.clusterify import StarClusterify
from my_info.cluster.reader import TwitterReader


class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args) != 1:
            print "Usage: python manage.py cluster <twitter_username>"
            return

        username = args[0]
        reader = TwitterReader(username)

        #list(reader.texts())
        try:
            #clusterify = SpectralClusterify(reader)
            clusterify = StarClusterify(reader)
            clusterify.annotate()
            clusterify.do_cluster()
        except:
            import traceback
            traceback.print_exc()
