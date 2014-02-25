# coding=utf-8
from collections import defaultdict
from my_info.cluster.datatxt import DataTXT


class Annotator(object):
    def __init__(self, items):
        self.texts = [x[0] for x in items]
        self.urls = [x[1] for x in items]
        self.user = [x[2] for x in items]
        self.datatxt = DataTXT()

    def annotate(self, test=None):
        """
        # >>> a = Annotator([('mozilla funziona peggio di google chrome', '')])
        # >>> a.annotate(test="annotations")
        # [u'http://it.wikipedia.org/wiki/Mozilla', \
# u'http://it.wikipedia.org/wiki/Google_Chrome']
        >>> a = Annotator([('@mozilla funziona peggio di google chrome', '')])
        >>> a.annotate(test="annotations")
        [u'http://it.wikipedia.org/wiki/Google_Chrome']
        # >>> a = Annotator([('mozilla funziona peggio di @google_chrome', '')])
        # >>> a.annotate(test="annotations")
        # [u'http://it.wikipedia.org/wiki/Mozilla']
        # >>> a = Annotator([('@mozilla funziona peggio di @google_chrome', '')])
        # >>> a.annotate(test="annotations")
        # []
        """
        tweets = defaultdict(list)

        annotated_texts_tmp = []

        for i, text in enumerate(self.texts):
            text_ann = []
            for x in text.split('\s'):
                if x.startswith('@'):
                    x = "_" * len(x)
                text_ann.append(x)

            text_ann = u" ".join(text_ann)
            annotation = self.datatxt.nex(text_ann)

            if annotation is None:
                continue

            d = {
                'text': text,
                'url': self.urls[i],
                'user': self.user[i],
                'annotations': annotation['annotations'].values(),
            }

            for topics, ann in annotation['annotations'].items():
                annotation['annotations'][topics] = ann['confidence']
                tweets[topics].append(d)

            annotated_texts_tmp.append(annotation)

        annotated_texts = {
            x['id']: x for x in annotated_texts_tmp if x is not None
        }

        for k, v in annotated_texts.iteritems():
            del v['id']

        if test == "annotations":
            return annotated_texts.values()[0]['annotations'].keys()

        return annotated_texts, tweets