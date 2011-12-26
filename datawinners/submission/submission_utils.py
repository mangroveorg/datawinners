from django.utils import translation
from mangrove.form_model.form_model import get_form_model_by_code, FORM_CODE

class PostSMSProcessorLanguageActivator(object):
    def __init__(self, dbm,request):
        self.dbm = dbm
        self.request=request

    def process(self, form_code, submission_values):
        self.request[FORM_CODE]=form_code
        form_model = get_form_model_by_code(self.dbm, form_code)
        translation.activate(form_model.activeLanguages[0])


