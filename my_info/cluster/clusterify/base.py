class BaseClusterify(object):
    def __init__(self, reader):
        self.reader = reader

    def annotate(self):
        # annota i texts con dataTXT
        pass

    def do_cluster(self):
        raise NotImplemented