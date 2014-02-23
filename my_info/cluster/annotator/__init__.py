from collections import defaultdict
from my_info.cluster.datatxt import DataTXT


class Annotator(object):
    def __init__(self, texts):
        self.texts = texts
        self.datatxt = DataTXT()

    def annotate(self):
        tweets = defaultdict(list)

        annotated_texts_tmp = []
        start = '<span class="annotated-entity">'
        start_len = len(start)
        end = '</span>'
        end_len = len(end)

        for text in self.texts:
            annotation = self.datatxt.nex(text)
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
                tweets[topics].append(text)

            annotated_texts_tmp.append(annotation)

        annotated_texts = {
            x['id']: x for x in annotated_texts_tmp if x is not None
        }

        for k, v in annotated_texts.iteritems():
            del v['id']

        return annotated_texts, tweets
