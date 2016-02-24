

class EditLabelRule(object):

    def __init__(self):
        self.fields = []

    def apply(self):
        pass

    def update_xform(self, old_questionnaire, new_questionnaire):
        for old_field in old_questionnaire.fields:
            new_field = [new_field for new_field in new_questionnaire.fields if new_field.name == old_field.name]
            if new_field and new_field[0].label != old_field.label:
                old_questionnaire.xform = old_questionnaire.xform.replace(old_field.label, new_field[0].label)
