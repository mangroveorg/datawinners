
class SubjectTemplateValidator(object):
    def __init__(self, form_model):
        self.form_model = form_model

    def validate(self, values):

        template_questions = values.keys()
        form_fields = [field['code'] for field in self.form_model.form_fields]
        if template_questions != form_fields:
            raise Exception("Template mismatch")