from django.core.management import BaseCommand
from my_info.cluster.cache import RedisCache


class Command(BaseCommand):
    def handle(self, *args, **options):
        red = RedisCache()
        red.cleanup()
