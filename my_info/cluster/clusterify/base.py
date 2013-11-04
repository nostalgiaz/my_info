class BaseClusterify(object):
    def __init__(self, texts):
        self.texts = texts

    def annotate(self):
        # annota i texts con dataTXT
        pass

    def do_cluster(self):
        raise NotImplemented