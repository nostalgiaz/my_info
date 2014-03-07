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
        self.n_topic = 0
        self.pages = []
        self.topic_set = defaultdict(int)
        self.rel_matrix = []
        self.k = k
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
                self.n_topic += 1.
                self.pages.append(page)

    def _generate_adjagent_matrix(self):
        self._generate_topic_set()

        logger.info("topic set")
        logger.info(self.topic_set)

        rel = zeros((len(self.topic_set), len(self.topic_set)))
        degree = zeros(len(self.topic_set))

        for i, topic1 in enumerate(self.topic_set):
            for j, topic2 in enumerate(self.topic_set):
                if j > i:
                    rel_value = self.datatxt.rel(topic1, topic2)
                    rel[i][j] = rel_value
                    rel[j][i] = rel_value
                    degree[i] += rel_value
                    degree[j] += rel_value

        self.rel_matrix = rel

        return rel, degree

    def _generate_cluster_from_ids(self, ids):
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