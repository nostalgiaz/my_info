from collections import defaultdict
from numpy import zeros
from numpy.random import seed
from celery.utils.log import get_task_logger

from my_info.cluster.annotator import Annotator
from my_info.cluster.datatxt import DataTXT

logger = get_task_logger(__name__)


class BaseClusterify(object):
    def __init__(self, reader, k=None):
        self.reader = reader
        self.datatxt = DataTXT()
        self.snippets = []
        self.pages = []
        self.topic_set = defaultdict(int)
        self.rel_matrix = []
        self.k = k
        self.topics = []
        seed((1000, 2000))

    def annotate(self):
        annotator = Annotator(self.reader.texts())
        self.snippets, tweets = annotator.annotate()
        return tweets

    def _generate_topic_set(self):
        logger.info("snippet set")
        logger.info(self.snippets)
        for _, snippet in self.snippets.iteritems():
            for page, _ in snippet.get('annotations').iteritems():
                self.topic_set[page] += 1.

    def _generate_adjagent_matrix(self):
        self._generate_topic_set()

        logger.info("topic set")
        logger.info(self.topic_set)

        topics = self.topic_set.keys()
        rel = zeros((len(topics), len(topics)))

        BATCH_SIZE = 10
        for offsetX in xrange(0, len(topics), BATCH_SIZE):
            for offsetY in xrange(offsetX, len(topics), BATCH_SIZE):
                topicsX = topics[offsetX: offsetX + BATCH_SIZE]
                topicsY = topics[offsetY: offsetY + BATCH_SIZE]
                rel_values = self.datatxt.rel(topicsX, topicsY)
                for i in xrange(0, len(topicsX)):
                    for j in xrange(0, len(topicsY)):
                        rel[offsetX + i][offsetY + j] = rel_values[i][j]
                        rel[offsetY + j][offsetX + i] = rel_values[i][j]

        self.rel_matrix = rel

        return rel

    def _generate_cluster(self, ids):
        response = {}

        for i, id in enumerate(ids):
            if id in response:
                response[id].append(list(self.topic_set)[i])
            else:
                response[id] = [list(self.topic_set)[i]]

        return response

    def _generate_output_response(self, response):
        if not self.topic_set:
            self._generate_topic_set()

        response_dict = []

        for cluster in response.values():
            tmp = {}
            for topic in cluster:
                tmp[topic] = self.topic_set[topic] ** .5
            response_dict.append(tmp)

        return {
            'clusters': response_dict
        }

    def do_cluster(self):
        raise NotImplemented
