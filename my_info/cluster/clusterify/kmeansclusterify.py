from numpy import array, identity

from scipy.linalg import eig
from scipy.cluster.vq import kmeans2

from my_info.cluster.clusterify.base import BaseClusterify


class KMeansClusterify(BaseClusterify):
    def __init__(self, reader, k):
        super(KMeansClusterify, self).__init__(reader=reader, k=k)

    def _generate_cluster(self, laplatian_matrix):
        evals, evcts = eig(laplatian_matrix)
        edict = dict(zip(evals, evcts.transpose()))
        evals = sorted(edict.keys())

        return kmeans2(
            array([edict[k] for k in evals[1:3]]).transpose(), self.k
        )[1]

    def do_cluster(self):
        rel, degree = self._generate_adjagent_matrix()
        laplatian_matrix = degree * identity(len(degree)) - rel
        ids = self._generate_cluster(laplatian_matrix)
        response = self._generate_cluster_from_ids(ids)
        return self._generate_output_response(response)
