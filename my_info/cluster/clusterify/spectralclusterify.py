from sklearn.cluster import spectral_clustering

from my_info.cluster.clusterify.base import BaseClusterify


class SpectralClusterify(BaseClusterify):
    def __init__(self, reader, k):
        super(SpectralClusterify, self).__init__(reader=reader, k=k)

    def do_cluster(self):
        rel, _ = self._generate_adjagent_matrix()
        ids = spectral_clustering(rel, self.k)
        response = self._generate_cluster_from_ids(ids)
        return self._generate_output_response(response)