from django.core.management import BaseCommand

from my_info.cluster.reader import TwitterReader


class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args) != 1:
            print "Usage: python manage.py cluster <twitter_username>"
            return

        reader = TwitterReader(args[0])

        print list(reader.texts())
        clusterify = KMeanClusterify(reader.texts())
        print clusterify.do_cluster()
