from my_info.cluster.annotator import Annotator
from my_info.cluster.datatxt import DataTXT


class BaseClusterify(object):
    def __init__(self, reader):
        self.reader = reader
        self.datatxt = DataTXT()
        self.snippets = []

    def annotate(self):
        annotator = Annotator(self.reader.texts())
        self.snippets = annotator.annotate()
        return self.snippets

    def do_cluster(self):
        raise NotImplemented