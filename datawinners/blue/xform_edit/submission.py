from celery import group
from datawinners.main.database import get_db_manager
from datawinners.tasks import app
from mangrove.datastore.documents import SurveyResponseDocument

from mangrove.transport.contract.survey_response import SurveyResponse


@app.task(max_retries=1, throw=False, track_started=True)
def update_all(database_name, rules, questionnaire_id):
    manager = get_db_manager(database_name)
    rows = manager.database.iterview("surveyresponse/surveyresponse", 1000, reduce=False, include_docs=False,
                                          startkey=[questionnaire_id], endkey=[questionnaire_id, {}])

    jobs = group(process_submission.s(database_name, rules, row) for row in rows)
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