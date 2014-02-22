from collections import defaultdict
from my_info.cluster.datatxt import DataTXT


class Annotator(object):
    def __init__(self, texts):
        self.texts = texts
        self.datatxt = DataTXT()

    def annotate(self):
        tweets = defaultdict(list)

        annotated_texts_tmp = []

        for text in self.texts:
            print text
            annotation = self.datatxt.nex(text)

            if annotation is None:
                continue

            for topics, _ in annotation['annotations'].iteritems():
                print "* " + topics
                tweets[topics].append(text)

            annotated_texts_tmp.append(annotation)

        annotated_texts = {
            x['id']: x for x in annotated_texts_tmp if x is not None
        }

        for k, v in annotated_texts.iteritems():
            del v['id']

        return annotated_texts, tweets
