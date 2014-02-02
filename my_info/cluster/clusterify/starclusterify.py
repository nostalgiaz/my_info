# from collections import defaultdict
from my_info.cluster.clusterify.base import BaseClusterify


class StarClusterify(BaseClusterify):
    def __init__(self, reader):
        super(StarClusterify, self).__init__(reader=reader)

    def do_cluster(self):
        beta = .5
        topics = {}

        for snippet in self.snippets:
            confidence = snippet.get('confidence')

            for ann_index, annotation in enumerate(snippet.get('annotations')):
                topic = topics.get(annotation)
                if topic is None:
                    topic = {
                        'page': annotation,
                        'score': 0,
                        'tweets': [],
                        'rel': 0,  # ?
                    }
                else:
                    topic['score'] += confidence[ann_index]
                topic['tweets'].append(snippet)
                topics[annotation] = topic

        ranked_topic = [value for key, value in topics.iteritems()]

        ranked_topic_sorted = sorted(
            ranked_topic,
            key=lambda x: x['score'],
        )

        clusters = []

        for topic in ranked_topic_sorted:
            merged = False

            for cluster_index, cluster in enumerate(clusters):
                rel = self.datatxt.rel(topic['page'], cluster['main']['page'])

                if rel > beta:
                    cluster['topics'].append(topic)
                    cluster['tweets'] += topic['tweets']
                    topic['rel'] = rel
                    merged = True
                    break

            if not merged:
                clusters.append({
                    'main': topic,
                    'topics': [topic],
                    'tweets': topic['tweets'],
                })

        for cluster in clusters:
            elements = []

            if not "topics" in cluster:
                continue

            for topic in cluster['topics']:
                #print topic
                elements.append({
                    'id': topic['page'],
                    'score': topic['score'],
                    'rel': topic['rel'],  # if 'rel' in topic else None,  # ?
                    'title': topic['page'],
                    'tweets': [tweet['id'] for tweet in topic['tweets']],
                })

            clusters.append({
                'elements': elements,
                'tweets': [tweet['id'] for tweet in cluster['tweets']]
            })

        result = {}

        for cluster in clusters:
            if not "main" in cluster:
                continue
            result[cluster['main']['page']] = {
                'title': cluster['main']['page'],
                'items': [r['page'] for r in cluster['topics']]
            }

        print result
        return result