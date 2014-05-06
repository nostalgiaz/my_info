# coding=utf-8
import re

from collections import defaultdict
from celery.utils.log import get_task_logger
from my_info.cluster.datatxt import DataTXT

logger = get_task_logger(__name__)


class Annotator(object):
    def __init__(self, items):
        self.texts = [x[0] for x in items]
        self.urls = [x[1] for x in items]
        self.user = [x[2] for x in items]
        self.datatxt = DataTXT()

    def annotate(self, test=None):
        """
        >>> a = Annotator([('mozilla funziona google chrome', '', '')])
        >>> a.annotate(test="annotations")
        [u'http://en.wikipedia.org/wiki/Google_Chrome', u'http://en.wikipedia.org/wiki/Mozilla']
        >>> a = Annotator([('@mozilla funziona google chrome', '', '')])
        >>> a.annotate(test="annotations")
        [u'http://en.wikipedia.org/wiki/Google_Chrome']
        >>> a = Annotator([('mozilla funziona @google_chrome', '', '')])
        >>> a.annotate(test="annotations")
        [u'http://en.wikipedia.org/wiki/Mozilla']
        >>> a = Annotator([('@mozilla funziona @google_chrome', '', '')])
        >>> a.annotate(test="annotations")
        []
        >>> a = Annotator([('@google funziona http://google.com', '', '')])
        >>> a.annotate(test="annotations")
        []
        """
        t_set = set()
        tweets = defaultdict(list)

        annotated_texts_tmp = []
        rew = "((https?|ftp)://|(www|ftp)\.)[a-z0-9-]+(\.[a-z0-9-]+)+([/?].*)?"

        for i, text in enumerate(self.texts):
            text_ann = []
            for x in text.split(' '):
                if x.startswith('@'):             # username
                    x = "_" * len(x)
                else:                             # website
                    match = re.search(rew, x)
                    if match:
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

            nice_page = {}
            for topics, ann in annotation['annotations'].items():
                page = topics
                if '://it.' in topics:  # italian entity
                    page = self.datatxt.interWikiRecon.get_inter_wikilinks(
                        topics).get('EN')

                    if page is None:
                        page = topics
                    else:
                        nice_page[page] = ann['confidence']
                else:
                    nice_page[page] = ann['confidence']

                tweets[page].append(d)

            del annotation['annotations']
            annotation['annotations'] = nice_page
            annotated_texts_tmp.append(annotation)

        annotated_texts = {
            x['id']: x for x in annotated_texts_tmp if x is not None
        }

        for k, v in annotated_texts.iteritems():
            del v['id']

        if test == "annotations":
            return annotated_texts.values()[0]['annotations'].keys()

        return annotated_texts, tweets