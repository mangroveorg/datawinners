import logging

from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport.contract.survey_response import SurveyResponse

from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from migration.couch.utils import migrate, mark_as_completed


def make_survey_response_link_to_document_id(db_name):
    dbm =get_db_manager(db_name)
    logger = logging.getLogger(db_name)
    survey_responses = dbm.load_all_rows_in_view("survey_response_by_survey_response_id", include_docs=True)
    survey_responses = [SurveyResponse.new_from_doc(dbm=dbm, doc=SurveyResponse.__document_class__.wrap(survey_response['value'])) for survey_response in survey_responses]
    try:
        for survey_response in survey_responses:
            if survey_response.form_code:
                form_model = get_form_model_by_code(dbm, survey_response.form_code)
                del survey_response._doc['form_code']
                survey_response._doc['form_model_id'] = form_model.id
                survey_response._dbm._save_document(survey_response._doc, process_post_update=False)
            else:
                logger.info("form_code not present in survey response:"+survey_response.id)
    except Exception as e:
        logger.error(e.message + db_name)
    mark_as_completed(db_name)

migrate(all_db_names(), make_survey_response_link_to_document_id, version=(13,1,1), threads=1)