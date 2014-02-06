from collections import defaultdict
import numpy as np
from scipy.linalg import eig
from scipy.cluster.vq import kmeans2

from my_info.cluster.clusterify.base import BaseClusterify


class KMeansClusterify(BaseClusterify):
    def __init__(self, reader):
        super(KMeansClusterify, self).__init__(reader=reader)

    def _rename_clusters(self, idx):
        num = -1
        seen = {}
        newidx = []

        for id in idx:
            if id not in seen:
                num += 1
                seen[id] = num
            newidx.append(seen[id])
        return np.array(newidx)

    def _cluster_points(self, laplatian_matrix):
        evals, evcts = eig(laplatian_matrix)
        evals, evcts = evals.real, evcts.real
        edict = dict(zip(evals, evcts.transpose()))
        evals = sorted(edict.keys())

        _, idx = kmeans2(
            np.array([edict[k] for k in evals[1:3]]).transpose(),
            6
        )
        return self._rename_clusters(idx)

    def do_cluster(self):
        np.set_printoptions(precision=2, suppress=True, linewidth=200)
        topic_set = defaultdict(int)
        n_topic = 0
        pages = []

        for _, snippet in self.snippets.iteritems():
            for page, _ in snippet.get('annotations').iteritems():
                topic_set[page] += 1.
                n_topic += 1.
                pages.append(page)

        rel = np.zeros((len(topic_set), len(topic_set)))
        rel_row = np.zeros(len(topic_set))

        for i, topic1 in enumerate(topic_set):
            for j, topic2 in enumerate(topic_set):
                if j > i:
                    rel_value = self.datatxt.rel(topic1, topic2)
                    rel[i][j] = rel_value
                    rel[j][i] = rel_value
                    rel_row[i] += rel_value
                    rel_row[j] += rel_value

        laplatian_matrix = rel_row * np.identity(len(rel_row)) - rel

        idx = self._cluster_points(laplatian_matrix)

        response = {}
        for i, id in enumerate(idx):
            if id in response:
                response[id].append(list(topic_set)[i])
            else:
                response[id] = [list(topic_set)[i]]

        return [{'topics': x} for x in response.values()]
