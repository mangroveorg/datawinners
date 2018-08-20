class UnsupportedXformEditException(Exception):
    def __init__(self):
        self.message = "Unsupported xlsform edit exception"


class XFormEditor(object):
    def __init__(self, submission, validator, questionnaire):
        self.submission = submission
        self.validator = validator
        self.questionnaire = questionnaire

    def edit(self, new_questionnaire, old_questionnaire, activity_log_detail):
        if not self.validator.valid(new_questionnaire, old_questionnaire, activity_log_detail):
            raise UnsupportedXformEditException()

        self.questionnaire.save(new_questionnaire)

        self.submission.update_all(new_questionnaire.id)

        # TODO: send email only if new unique id added?
