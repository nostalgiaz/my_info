from collections import defaultdict
import numpy as np

from my_info.cluster.annotator import Annotator
from my_info.cluster.clusterify.base import BaseClusterify
from my_info.cluster.datatxt import DataTXT


class KMeanClusterify(BaseClusterify):
    def __init__(self, reader):
        self.annotations = []
        self.datatxt = DataTXT()
        super(KMeanClusterify, self).__init__(reader=reader)

    def annotate(self):
        annotator = Annotator(self.reader.texts())
        self.annotations = annotator.annotate()
        return self.annotations

    def _cut(self, set1, set2):
        sum_ = 0
        for tc in set1:
            for td in set2:
                sum_ += self.datatxt.rel(tc, td)

        return sum_

    def _vol(self, set1):
        sum_ = 0
        for tc in set1:
            for td in set1:
                sum_ += self.datatxt.rel(tc, td)

        return sum_

    def _ncut(self, sorted_nodes):
        min_index = None
        min_ = None

        for i in range(1, len(sorted_nodes)):
            val = self._cut(sorted_nodes[:i], sorted_nodes[i:]) / self._vol(sorted_nodes[:i])
            if min_ is None or min_ > val:
                min_index = i
                min_ = val

        return min_index

    def do_cluster(self):
        topic_set = defaultdict(int)
        n_snippets = len(self.annotations)
        k_size = 10
        # snippet = tweet
        # topic = entity

        for snippet in self.annotations:
            for topic in snippet['annotations']:
                topic_set[topic] += 1

        topic_set = {
            key: value for key, value in topic_set.items()
            if value <= n_snippets * .5
        }

        big_clusters = [topic_set.keys()]
        while len(big_clusters) <= k_size or len(topic_set) == len(big_clusters):
            print len(big_clusters), big_clusters
            min_eigenvalue = None
            min_eigenvector = None
            selected_cluster_index = None

            for cluster_index, big_cluster in enumerate(big_clusters):
                if len(big_cluster) == 1:
                    continue
                matrix = np.zeros((len(big_cluster), len(big_cluster)))
                for i, topic1 in enumerate(big_cluster):
                    matrix[i][i] = 1.
                    for j, topic2 in enumerate(big_cluster):
                        if j > i:
                            matrix[i][j] = self.datatxt.rel(topic1, topic2)
                            matrix[j][i] = matrix[i][j]

                laplatian_matrix = np.identity(len(big_cluster)) - matrix  # ?

                # ?
                eigenvalues, eigenvectors = np.linalg.eig(laplatian_matrix)

                eigenvalue = eigenvalues[2]

                if min_eigenvalue is None or eigenvalue < min_eigenvalue:
                    min_eigenvalue = eigenvalue
                    min_eigenvector = eigenvectors[2]
                    selected_cluster_index = cluster_index

            selected_cluster = big_clusters[selected_cluster_index]
            sorted_nodes = sorted(
                enumerate(selected_cluster),
                key=lambda x: min_eigenvector[x[0]]
            )

            sorted_nodes = [x[1] for x in sorted_nodes]
            cut = self._ncut(sorted_nodes)
            big_clusters = [
                cluster for cluster in big_clusters
                if cluster != selected_cluster
            ] + [selected_cluster[:cut], selected_cluster[cut:]]

            #print matrix
            #print laplatian_matrix

        # trovare i big cluster
        # per ogni big cluster:
            # trova la matrice normalizzata di laplace
            # calcola il secondo eigenvalue
            # scegli il big cluster che ha secondo eigenvalue minore
        # ordinare i nodi del bigcluster in base alla loro proiezione sul loro
                # eigenvector
        # tagliare nel punto che minimizza la sommatoria n Ncut


        return big_clusters
