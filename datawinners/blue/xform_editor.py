from datawinners.blue.xform_edit.submission import update_all

class UnsupportedXformEditException(Exception):
    def __init__(self):
        self.message = "Unsupported xlsform edit exception"


class XFormEditor(object):
    def __init__(self, dbname, rules, validator, questionnaire):
        self.dbname = dbname
        self.rules = rules
        self.validator = validator
        self.questionnaire = questionnaire

    def edit(self, new_questionnaire, old_questionnaire, activity_log_detail):
        if not self.validator.valid(new_questionnaire, old_questionnaire, activity_log_detail):
            raise UnsupportedXformEditException()

        self.questionnaire.save(new_questionnaire)

        update_all.delay(self.dbname, self.rules, new_questionnaire.id)

        # TODO: send email only if new unique id added?
