from collections import defaultdict
import numpy as np
import pprint
from networkx import Graph, normalized_laplacian_matrix
from sklearn.cluster import spectral_clustering

from my_info.cluster.clusterify.base import BaseClusterify


class SpectralClusterify(BaseClusterify):
    def __init__(self, reader):
        self.first_time = True
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
        #print len(sorted_nodes)
        if len(sorted_nodes) <= 2:
            return 1

        for i in range(1, len(sorted_nodes)):
            val = self._cut(sorted_nodes[:i], sorted_nodes[i:]) * (1/self._vol(sorted_nodes[:i]) + 1/self._vol(sorted_nodes[i:]))
            if not min_ or min_ > val:
                min_ = val
                min_index = i
        return min_index

    def do_cluster(self):
        pp = pprint.PrettyPrinter(indent=4)
        np.set_printoptions(precision=2, suppress=True, linewidth=200)
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

        #big_clusters = [topic_set.keys()]
        #while len(big_clusters) <= k_max or len(topic_set) == len(big_clusters):
        #    min_eigenvalue = None
        #    min_eigenvector = None
        #    selected_cluster_index = None
        #
        #    for cluster_index, big_cluster in enumerate(big_clusters):
        #        if len(big_cluster) == 1:
        #            continue

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

        idx = spectral_clustering(rel, 5)
        response = {}
        for i, id in enumerate(idx):
            if id in response:
                response[id].append(list(topic_set)[i])
            else:
                response[id] = [list(topic_set)[i]]

        return [{'topics': x} for x in response.values()]

        #        if self.first_time:
        #            big_cluster = [x for i, x in enumerate(big_cluster) if rel_row[i] > 0]
        #            rel = np.zeros((len(big_cluster), len(big_cluster)))
        #            rel_row = np.zeros(len(big_cluster))
        #            for i, topic1 in enumerate(big_cluster):
        #                for j, topic2 in enumerate(big_cluster):
        #                    if j > i:
        #                        rel_value = self.datatxt.rel(topic1, topic2)
        #                        rel[i][j] = rel_value
        #                        rel[j][i] = rel_value
        #                        rel_row[i] += rel_value
        #                        rel_row[j] += rel_value
        #
        #            big_clusters[cluster_index] = big_cluster
        #            self.first_time = False
        #
        #        #for i, t in enumerate(big_cluster):
        #        #    print t, rel[i]
        #
        #        #for i, row in enumerate(rel_row):
        #        #    if row == 0:
        #        #        for j in range(len(rel_row)):
        #        #            del rel[i][j]
        #        #        del rel_row[i]
        #        #        del rel[i]
        #
        #
        #        #for i in range(len(big_cluster)):
        #        #    for j in range(len(big_cluster)):
        #        #        rel_row[i] += rel[i][j] + rel[j][i]
        #
        #        #print
        #        #print rel_row
        #        #return
        #
        #        #mode = 2
        #        #if mode == 1:
        #        #    d = np.identity(len(rel_row)) * rel_row ** -1
        #        #    print "d"
        #        #    print d
        #        #    l = d - rel
        #        #    print "l"
        #        #    print l
        #        #    laplatian_matrix = d * l
        #        #else:
        #        #laplatian_matrix = np.zeros(
        #        #    (len(big_cluster), len(big_cluster))
        #        #)
        #        #
        #        #for i in range(len(big_cluster)):
        #        #    for j in range(len(big_cluster)):
        #        #        if i == j or rel_row[i] <= 0:
        #        #            laplatian_matrix[i][j] = 0
        #        #        else:
        #        #            laplatian_matrix[i][j] = rel[i][j] / rel_row[i]
        #        #
        #        from math import sqrt
        #        laplatian_matrix = np.zeros((len(big_cluster), len(big_cluster)))
        #        for i in range(len(big_cluster)):
        #            for j in range(len(big_cluster)):
        #                if i == j and rel_row[i] != 0:
        #                    laplatian_matrix[i][j] = 1. - (rel[i][j] / rel_row[i])
        #                elif i != j and rel[i][j] > 0:
        #                    laplatian_matrix[i][j] = 0. - (rel[i][j] / sqrt(rel_row[i] * rel_row[j]))
        #
        #
        #        #print "laplatian"
        #        #print laplatian_matrix
        #
        #        #assert False
        #        #for x in range(len(laplatian_matrix)):
        #        #    laplatian_matrix[x][x] = 0
        #
        #        #print(laplatian_matrix)
        #        #return
        #        #return laplatian_matrix
        #        eigenvalues, eigenvectors = np.linalg.eig(laplatian_matrix)
        #
        #        #eigenvalues, eigenvectors = eigenvalues.real, eigenvectors.real
        #
        #        print "eigenvalues", eigenvalues
        #        print
        #        print "eigenvectors"
        #        print eigenvectors
        #        #return
        #
        #        sorted_eigen = sorted(
        #            zip(eigenvalues, eigenvectors.transpose()), key=lambda x: x[0],
        #            reverse=True
        #        )
        #        #print sorted_eigen
        #        #return
        #        second_eigenvalue = sorted_eigen[1][0]
        #
        #        #print "eigen", eigenvalues
        #        #print "proposta eigen", second_eigenvalue
        #        if min_eigenvalue is None or second_eigenvalue < min_eigenvalue:
        #            min_eigenvalue = second_eigenvalue
        #            min_eigenvector = sorted_eigen[1][1]
        #            selected_cluster_index = cluster_index
        #
        #
        #
        #    #print "selto eigen", min_eigenvalue
        #    selected_cluster = big_clusters[selected_cluster_index]
        #    #sele
        #
        #    #min_eigenvector = ((np.identity(len(rel_row)) * rel_row)).dot(min_eigenvector.transpose())
        #
        #    #d = (np.identity(len(rel_row)) * rel_row) ** .5
        #    #print d
        #    #print
        #    #d = (d)
        #    #print d
        #    #print
        #
        #    #min_eigenvector = d.dot(min_eigenvector)
        #    #print "#############"
        #    #print min_eigenvector
        #    #print d
        #    #print "#############"
        #    #min_eigenvector = min_eigenvector.dot(d)
        #
        #    print min_eigenvector
        #
        #    sorted_nodes = [x[1] for x in sorted(
        #        enumerate(selected_cluster),
        #        key=lambda x: min_eigenvector[x[0]]
        #    )]
        #
        #    print "min", min_eigenvalue
        #    debug_ = [
        #        (x[0], x[1], min_eigenvector[x[0]]) for x in
        #        sorted(enumerate(selected_cluster), key=lambda x: min_eigenvector[x[0]])
        #    ]
        #
        #    for x in debug_:
        #        print x
        #
        #
        #    cut = self._ncut(sorted_nodes)
        #    big_clusters = [
        #        cluster for cluster in big_clusters
        #        if cluster != selected_cluster
        #    ] + [sorted_nodes[:cut], sorted_nodes[cut:]]
        #    print "sorted nodes"
        #    pp.pprint(sorted_nodes)
        #    print "cut"
        #    print cut
        #    print "sorted nodes 1"
        #    pp.pprint(sorted_nodes[:cut])
        #    print "sorted nodes 2"
        #    pp.pprint(sorted_nodes[cut:])
        #    print "big cluster"
        #    pp.pprint(big_clusters)
        #    print "*" * 80
        #
        #
        #return big_clusters
