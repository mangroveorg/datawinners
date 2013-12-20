from celery import Celery
from datawinners.main.database import get_db_manager

from mangrove.transport.repository.survey_responses import survey_responses_by_form_code

app = Celery('tasks', backend='amqp', broker='amqp://')


@app.task
def update_associated_submissions(update_dict):
    manager = get_db_manager(update_dict['database_name'])
    survey_responses = survey_responses_by_form_code(manager, update_dict['old_form_code'])
    documents = []
    for survey_response in survey_responses:
        survey_response.form_code = update_dict['new_form_code']
        survey_response.form_model_revision = update_dict["new_revision"]
        documents.append(survey_response._doc)
    manager._save_documents(documents)