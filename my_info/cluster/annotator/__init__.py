from collections import defaultdict
from my_info.cluster.datatxt import DataTXT


class Annotator(object):
    def __init__(self, items):
        self.texts = [x[0] for x in items]
        self.urls = [x[1] for x in items]
        self.datatxt = DataTXT()

    def annotate(self, test=False):
        """
        >>> a = Annotator([('mozilla funziona peggio di google chrome', '')])
        >>> a.annotate(test=True)
        [u'http://it.wikipedia.org/wiki/Mozilla', \
u'http://it.wikipedia.org/wiki/Google_Chrome']
        >>> a = Annotator([('@mozilla funziona peggio di google chrome', '')])
        >>> a.annotate(test=True)
        [u'http://it.wikipedia.org/wiki/Google_Chrome']
        >>> a = Annotator([('mozilla funziona peggio di @google_chrome', '')])
        >>> a.annotate(test=True)
        [u'http://it.wikipedia.org/wiki/Mozilla']
        >>> a = Annotator([('@mozilla funziona peggio di @google_chrome', '')])
        >>> a.annotate(test=True)
        []
        """
        tweets = defaultdict(list)

        annotated_texts_tmp = []
        start = '<span class="annotated-entity">'
        start_len = len(start)
        end = '</span>'
        end_len = len(end)

        for i, text in enumerate(self.texts):

            text_ann = []
            for x in text.split():
                if x.startswith('@'):
                    x = "_" * len(x)
                text_ann.append(x)

            text_ann = " ".join(text_ann)
            annotation = self.datatxt.nex(text_ann)
            shift = 0

            if annotation is None:
                continue

            sortered_annotations = sorted(
                annotation['annotations'].items(),
                key=lambda x: x[1]['start']
            )

            for topics, ann in sortered_annotations:
                start_text = ann['start'] + shift
                end_text = ann['end'] + shift
                text = u"{}{}{}{}{}".format(
                    text[:start_text],
                    start,
                    text[start_text: end_text],
                    end,
                    text[end_text:]
                )

                annotation['annotations'][topics] = ann['confidence']
                shift += start_len + end_len

            for topics, _ in sortered_annotations:
                tweets[topics].append({
                    'text': text,
                    'url': self.urls[i],
                })

            annotated_texts_tmp.append(annotation)

        annotated_texts = {
            x['id']: x for x in annotated_texts_tmp if x is not None
        }

        for k, v in annotated_texts.iteritems():
            del v['id']

        if test:
            return annotated_texts.values()[0]['annotations'].keys()

        return annotated_texts, tweets