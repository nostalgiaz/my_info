from dandelion import datatxt, DandelionException
from my_info.settings import DATATXT_APP_ID, DATATXT_APP_KEY


class DataTXT(object):
    def __init__(self):
        self.datatxt = datatxt.DataTXT(
            app_id=DATATXT_APP_ID,
            app_key=DATATXT_APP_KEY,
        )

    def nex(self, *args):
        try:
            annotated = self.datatxt.nex(args[0])
            return {
                'lang': annotated.lang,
                'annotations': [ann.uri for ann in annotated.annotations]
            }
        except DandelionException:
            return {
                'lang': "undefined"
            }