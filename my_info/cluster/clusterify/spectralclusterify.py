from collections import defaultdict
import numpy as np
from networkx import Graph, normalized_laplacian_matrix

from my_info.cluster.clusterify.base import BaseClusterify


class SpectralClusterify(BaseClusterify):
    def __init__(self, reader):
        self.pruned = set()
        super(SpectralClusterify, self).__init__(reader=reader)

    def _cut(self, set1, set2):
        sum_ = 0.
        for tc in set1:
            for td in set2:
                sum_ += self.datatxt.rel(tc, td)

        return sum_

    def _vol(self, set1):
        sum_ = 0.
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
        #np.set_printoptions(precision=2, suppress=True, linewidth=200)
        topic_set = defaultdict(int)
        n_topic = 0
        max_coverage = .7
        rel_limit = .3
        #small_limit = 2
        n_snippets = len(self.snippets)
        pages = []
        k_max = 10

        for _, snippet in self.snippets.iteritems():
            for page, _ in snippet.get('annotations').iteritems():
                topic_set[page] += 1.
                n_topic += 1.
                pages.append(page)

        #deg = np.zeros(len(pages))
        #sym = np.zeros((len(pages), len(pages)))

        #for i, page1 in enumerate(pages):
        #    for j, page2 in enumerate(pages):
        #        if i <= j:
        #            continue
        #        else:
        #            rel = self.datatxt.rel(page1, page2)
        #
        #            if rel < rel_limit:
        #                continue
        #
        #            sym[i][j] = rel
        #            sym[j][i] = rel
        #            deg[j] += rel
        #            deg[i] += rel

        big_clusters = [topic_set.keys()]
        while len(big_clusters) <= k_max or len(topic_set) == len(big_clusters):
            min_eigenvalue = None
            min_eigenvector = None
            selected_cluster_index = None

            for cluster_index, big_cluster in enumerate(big_clusters):
                if len(big_cluster) == 1:
                    continue

                rel = np.zeros((len(big_cluster), len(big_cluster)))
                deg = np.zeros(len(big_cluster))
                #assert False, len(deg)

                for i, topic1 in enumerate(big_cluster):
                    for j, topic2 in enumerate(big_cluster):
                        if j > i:
                            rel_value = self.datatxt.rel(topic1, topic2)
                            # if?
                            rel[i][j] = rel_value
                            rel[j][i] = rel_value
                            deg[i] += rel_value
                            deg[j] += rel_value

                #assert False, deg

                #edges = []
                #for x, row in enumerate(rel):
                #    for i in range(len(row)):
                #        edges.append((x, i, rel[x][i]))
                #
                #g = Graph()
                #g.add_weighted_edges_from(edges)
                #laplatian_matrix = normalized_laplacian_matrix(g)
                #d_matrix = ([1/x ** .5 for x in deg] * np.identity(len(big_cluster)))
                #assert False, (d_matrix)
                #d_matrix = [(1/x)**.5 for x in deg] * np.identity(len(big_cluster))
                #laplatian_matrix = np.identity(len(big_cluster)) - (d_matrix * rel * d_matrix)  # ?

                rel_row = np.zeros(len(big_cluster))
                laplatian_matrix = np.zeros((len(big_cluster), len(big_cluster)))

                for i in range(len(big_cluster)):
                    for j in range(len(big_cluster)):
                        rel_row[i] += rel[i][j]

                for i in range(len(big_cluster)):
                    for j in range(len(big_cluster)):
                        if i == j or rel_row[i] <= 0:
                            laplatian_matrix[i][j] = 0
                        else:
                            laplatian_matrix[i][j] = rel[i][j] / rel_row[i]

                eigenvalues, eigenvectors = np.linalg.eig(laplatian_matrix)

                sorted_eigen = sorted(
                    zip(eigenvalues, eigenvectors), key=lambda x: x[0],
                    reverse=True
                )

                second_eigenvalue = sorted_eigen[1][0]

                if min_eigenvalue is None or min_eigenvalue > second_eigenvalue:
                    min_eigenvalue = second_eigenvalue
                    min_eigenvector = sorted_eigen[1][1]
                    selected_cluster_index = cluster_index

            selected_cluster = big_clusters[selected_cluster_index]

            sorted_nodes = [x[1] for x in sorted(
                enumerate(selected_cluster),
                key=lambda x: min_eigenvector[x[0]],
            )]

            cut = self._ncut(sorted_nodes)
            big_clusters = [
                cluster for cluster in big_clusters
                if cluster != selected_cluster
            ] + [sorted_nodes[:cut], sorted_nodes[cut:]]

        return big_clusters
