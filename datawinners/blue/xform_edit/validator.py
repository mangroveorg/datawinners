class Validator(object):
    def __init__(self, rules):
        self.rules = rules

    def valid(self, new_questionnaire, old_questionnaire):
        for rule in self.rules:
            rule.update_xform(old_questionnaire, new_questionnaire)
        old_questionnaire.xform_model.change_instance_id(new_questionnaire.xform_model)

        old_questionnaire.xform_model.sort()
        new_questionnaire.xform_model.sort()

        return old_questionnaire.xform_model.equals(new_questionnaire.xform_model)