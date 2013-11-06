from django.core.management import BaseCommand

from my_info.cluster.clusterify import KMeanClusterify
from my_info.cluster.reader import TwitterReader


class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args) != 1:
            print "Usage: python manage.py cluster <twitter_username>"
            return

        username = args[0]
        reader = TwitterReader(username)

        print list(reader.texts())
        clusterify = KMeanClusterify(reader)
        print clusterify.annotate()
        #print clusterify.do_cluster()
