from datawinners.blue.rules import REGISTERED_RULES


class UnsupportedXformEditException(Exception):
    def __init__(self):
        self.message = "Unsupported xlsform edit exception"

class XFormEditor(object):
    def edit(self, new_questionnaire, old_questionnaire):
        if not self._validate(new_questionnaire, old_questionnaire):
            raise UnsupportedXformEditException()

        old_questionnaire.save(process_post_update=False)
        # TODO: send email only if new unique id added?

    def _validate(self, new_questionnaire, old_questionnaire):
        for rule in REGISTERED_RULES:
            rule.update_xform(old_questionnaire, new_questionnaire)

        return old_questionnaire.xform_model.equals(new_questionnaire.xform_model)

    def _apply(self):
        pass
