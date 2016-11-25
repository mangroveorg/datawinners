from celery import group
from datawinners.main.database import get_db_manager
from datawinners.tasks import app
from mangrove.datastore.documents import SurveyResponseDocument
from mangrove.transport.contract.survey_response import SurveyResponse


class Submission(object):

    def __init__(self, manager, dbname, rules):
        self.manager = manager
        self.dbname = dbname
        self.rules = rules

    def update_all(self, questionnaire_id):
        rows = self.manager.database.iterview("surveyresponse/surveyresponse", 1000, reduce=False, include_docs=False,
                                              startkey=[questionnaire_id], endkey=[questionnaire_id, {}])

        jobs = group(process_submission.s(self.dbname, self.rules, row) for row in rows)
        jobs.apply_async()


@app.task(max_retries=1, throw=False, track_started=True)
def process_submission(database_name, rules, row):
    manager = get_db_manager(database_name)
    success = False
    submission = SurveyResponseDocument._wrap_row(row)
    for rule in rules:
        success = success or rule.update_submission(submission)
    if success:
        survey_response = SurveyResponse.new_from_doc(manager, submission)
        survey_response.save()
