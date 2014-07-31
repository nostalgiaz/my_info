from sklearn.cluster import Ward
from my_info.cluster.clusterify.base import BaseClusterify


class HierarchicalClusterify(BaseClusterify):
    def __init__(self, reader, k):
        super(HierarchicalClusterify, self).__init__(reader=reader, k=k)

    def do_cluster(self):
        relatedness_matrix = self._generate_adjagent_matrix()

        cluster = Ward(
            n_clusters=self.k
        ).fit(relatedness_matrix)

        response = self._generate_cluster(cluster.labels_)

        return self._generate_output_response(response)
