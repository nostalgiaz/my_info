from sklearn.cluster import SpectralClustering
from my_info.cluster.clusterify.base import BaseClusterify


class SpectralClusterify(BaseClusterify):
    def __init__(self, reader, k):
        super(SpectralClusterify, self).__init__(reader=reader, k=k)

    def do_cluster(self):
        relatedness_matrix = self._generate_adjagent_matrix()

        cluster = SpectralClustering(
            n_clusters=self.k,
            affinity="precomputed"
        ).fit(relatedness_matrix)

        response = self._generate_cluster(cluster.labels_)

        return self._generate_output_response(response)
