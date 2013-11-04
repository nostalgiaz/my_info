from my_info.cluster.clusterify.base import BaseClusterify


class KMeanClusterify(BaseClusterify):
    def __init__(self, texts):
        super(KMeanClusterify, self).__init__(texts=texts)

    def do_cluster(self):
        from cluster import KMeansClustering
        # annotare
        # 
