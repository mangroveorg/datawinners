from django.utils.translation import gettext as _


class DataExtractionResult(object):
    def __init__(self):
        self.success = True
        self.message = _("You can access the data in submissions field.")
        self.submissions = []