from mangrove.datastore.documents import SurveyResponseDocument

from mangrove.transport.contract.survey_response import SurveyResponse


class Submission(object):
    def __init__(self, manager, dbname, rules):
        self.manager = manager
        self.dbname = dbname
        self.rules = rules

    def update_all(self, questionnaire):
        rows = self.manager.database.iterview("surveyresponse/surveyresponse", 1000, reduce=False, include_docs=False,
                                              startkey=[questionnaire.id], endkey=[questionnaire.id, {}])

        for row in rows:
            success = False
            submission = SurveyResponseDocument._wrap_row(row)
            for rule in self.rules:
                success = success or rule.update_submission(submission)
            if success:
                survey_response = SurveyResponse.new_from_doc(self.manager, submission)
                survey_response.save()
