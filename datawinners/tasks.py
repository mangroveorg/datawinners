from celery import Celery
from celery.task import current
from datawinners.main.database import get_db_manager

from mangrove.transport.repository.survey_responses import survey_responses_by_form_code

app = Celery('tasks', backend='amqp', broker='amqp://guest@127.0.0.1:5672//')


@app.task(max_retries=5)
def update_associated_submissions(update_dict):
    try:
        manager = get_db_manager(update_dict['database_name'])
        survey_responses = survey_responses_by_form_code(manager, update_dict['old_form_code'])
        documents = []
        for survey_response in survey_responses:
            survey_response.form_code = update_dict['new_form_code']
            survey_response.form_model_revision = update_dict["new_revision"]
            documents.append(survey_response._doc)
        manager._save_documents(documents)
    except Exception as e:
        current.retry(exc = e)
