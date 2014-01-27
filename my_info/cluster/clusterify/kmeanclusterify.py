from cluster import KMeansClustering

from my_info.cluster.annotator import Annotator
from my_info.cluster.clusterify.base import BaseClusterify


class KMeanClusterify(BaseClusterify):
    def __init__(self, reader):
        super(KMeanClusterify, self).__init__(reader=reader)

    def annotate(self):
        annotator = Annotator(self.reader.texts())
        return annotator.annotate()

    def do_cluster(self):
        KMeanClusterify
