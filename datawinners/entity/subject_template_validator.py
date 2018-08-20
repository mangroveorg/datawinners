from django.utils.translation import gettext
from datawinners.exceptions import ImportValidationError
class SubjectTemplateValidator(object):
    def __init__(self, form_model):
        self.form_model = form_model

    def validate(self, values):

        template_questions = values.keys()
        form_fields = [field['code'].lower() for field in self.form_model.form_fields]
        if template_questions != form_fields:
            raise ImportValidationError(gettext("The columns you are importing do not match the current Questionnaire. Please download the latest template for importing."))