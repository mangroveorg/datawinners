import logging
from multiprocessing.pool import Pool

from mangrove.datastore.documents import FormModelDocument
from mangrove.form_model.form_model import FormModel
from mangrove.transport.contract.survey_response import SurveyResponse
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from migration.couch.utils import migrate, mark_as_completed


def _get_matching_form_model(surveyresponse_date, form_models):
    for form_model in form_models:
        if form_model._doc.created < surveyresponse_date:
            return form_model
    return None


def _get_form_models(dbm, survey_response):
    rows = dbm.load_all_rows_in_view('all_questionnaire', include_docs=True, key=survey_response._doc['form_code'])
    if rows:
        return [FormModel.new_from_doc(dbm, FormModelDocument.wrap(row["value"])) for row in rows]
    return None


def _get_survey_responses(dbm, is_large_account):
    extra_params = {
        'include_docs': True
    }

    if is_large_account:
        extra_params['stale'] = 'ok'

    return dbm.database.iterview("survey_response_by_survey_response_id/survey_response_by_survey_response_id", 80000,
                                 **extra_params)


def _process_survey_response(survey_response_doc, db_name):
    dbm = get_db_manager(db_name)
    logger = logging.getLogger(db_name)

    try:
        survey_response = SurveyResponse.new_from_doc(dbm=dbm, doc=SurveyResponse.__document_class__.wrap(
            survey_response_doc['doc']))
        if 'form_code' not in survey_response._doc:
            logger.error("form_code not present in survey response:%s" % survey_response.uuid)
            return
        form_models = _get_form_models(dbm, survey_response)
        if not form_models:
            logger.error("No Questionnaire found for survey response:%s with form_code: %s" %
                         survey_response.uuid, survey_response._doc['form_code'])
        elif len(form_models) > 1:
            form_models.sort(key=lambda form_model: form_model._doc.created, reverse=True)
            matching_form_model = _get_matching_form_model(survey_response.created, form_models)
            if matching_form_model:
                del survey_response._doc['form_code']
                survey_response.form_model_id = matching_form_model.id
                survey_response.save(process_post_update=False)
            else:
                logger.error(
                    "No Questionnaire found with matching date for survey response: %s and form_code:%s" % survey_response.uuid,
                    survey_response._doc['form_code'])
        elif len(form_models) == 1:
            del survey_response._doc['form_code']
            survey_response.form_model_id = form_models[0].id
            survey_response.save(process_post_update=False)

    except Exception as e:
        logger.exception("Exception for survey response:%s" % survey_response.uuid)


def make_survey_response_link_to_form_model_document_id(db_name):
    dbm = get_db_manager(db_name)
    logger = logging.getLogger(db_name)
    is_large_account = db_name in ['hni_palme_flm546389', 'hni_usaid-mikolo_lei526034']
    process_count = 6 if is_large_account else 4
    p = Pool(processes=process_count)
    try:
        for survey_response_doc in _get_survey_responses(dbm, is_large_account):
            p.apply(_process_survey_response, (survey_response_doc, db_name))
    except Exception as e:
        logger.exception(db_name)
    p.close()
    p.join()
    mark_as_completed(db_name)

migrate(all_db_names(), make_survey_response_link_to_form_model_document_id, version=(13, 1, 1), threads=2)