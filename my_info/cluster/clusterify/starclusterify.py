from my_info.cluster.clusterify.base import BaseClusterify


class StarClusterify(BaseClusterify):
    def __init__(self, reader):
        super(StarClusterify, self).__init__(reader=reader)

    def do_cluster(self):
        min_relatedness_required = .3
        clusters = []
        topics = {}

        for id, snippet in self.snippets.iteritems():
            for page, confidence in snippet.get('annotations').iteritems():
                topic = topics.get(page)

                if topic is None:
                    topic = {'score': 0, 'tweets': []}
                else:
                    topic['score'] += confidence
                topic['tweets'].append(id)
                topics[page] = topic

        ranked_topic = sorted(
            topics.iteritems(),
            key=lambda (k, v): v['score'],
            reverse=True
        )

        for page, topic in ranked_topic:
            merged = False

            for cluster in clusters:
                rel = self.datatxt.rel(page, cluster['page'])

                if rel > min_relatedness_required:
                    cluster['topics'].append(page)
                    cluster['tweets'] += topic['tweets']
                    merged = True
                    break

            if not merged:
                clusters.append({
                    'page': page,
                    'topics': [page],
                    'tweets': topic['tweets'],
                })

        return self._generate_output_response({
            c['page']: c['topics'] for c in clusters
        })