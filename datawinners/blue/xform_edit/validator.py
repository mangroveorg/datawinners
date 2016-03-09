from datawinners.blue.rules import REGISTERED_RULES


class Validator(object):
    def valid(self, new_questionnaire, old_questionnaire):
        for rule in REGISTERED_RULES:
            rule.update_xform(old_questionnaire, new_questionnaire)

        return old_questionnaire.xform_model.equals(new_questionnaire.xform_model)