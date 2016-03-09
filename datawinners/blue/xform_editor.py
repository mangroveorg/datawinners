from datawinners.blue.rules import REGISTERED_RULES


class UnsupportedXformEditException(Exception):
    def __init__(self):
        self.message = "Unsupported xlsform edit exception"


class XFormEditor(object):
    def __init__(self, submission, submission_search, validator, questionnaire):
        self.submission = submission
        self.submission_search = submission_search
        self.validator = validator
        self.questionnaire = questionnaire

    def edit(self, new_questionnaire, old_questionnaire):
        if not self.validator.valid(new_questionnaire, old_questionnaire):
            raise UnsupportedXformEditException()

        self.questionnaire.save(new_questionnaire)

        self.submission_search.update_mapping(new_questionnaire)

        self.submission.update_all(new_questionnaire)

        # TODO: send email only if new unique id added?
