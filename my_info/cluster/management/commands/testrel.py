from django.core.management import BaseCommand
from my_info.cluster.datatxt import DataTXT


class Command(BaseCommand):
    def handle(self, *args, **options):
        datatxt = DataTXT()

        termodinamica_it = "http://it.wikipedia.org/wiki/Termodinamica"
        treno_it = "http://it.wikipedia.org/wiki/Treno"
        termodinamica_en = "http://en.wikipedia.org/wiki/Thermodynamics"
        treno_en = "http://en.wikipedia.org/wiki/Train"

        print datatxt.rel(termodinamica_it, treno_it)
        print datatxt.rel(termodinamica_it, treno_en)
        print datatxt.rel(termodinamica_en, treno_it)
        print datatxt.rel(termodinamica_en, treno_en)
#