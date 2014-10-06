import logging
from sets import Set

from mangrove.datastore.cache_manager import get_cache_manager
from mangrove.datastore.documents import FormModelDocument
from mangrove.form_model.form_model import FormModel, get_form_model_cache_key
from mangrove.transport.contract.survey_response import SurveyResponse
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from migration.couch.utils import migrate, mark_as_completed


def _get_matching_form_model(surveyresponse_date, form_models):
    for form_model in form_models:
        if form_model._doc.created < surveyresponse_date:
            return form_model
    return None

# LARGE_ACCOUNTS = ['hni_palme_flm546389', 'hni_usaid-mikolo_lei526034', 'hni_psi_dmf792011']

# def _set_stale_state_for_large_accounts(database_name):
#     extra_params = {}
#     if database_name in LARGE_ACCOUNTS:
#         extra_params['stale'] = 'ok'
#
#     return extra_params

FORM_MODEL_EXPIRY_TIME_IN_SEC = 60 * 60


def _fetch_form_model_docs_from_couch(dbm, form_code):
    # extra_params = _set_stale_state_for_large_accounts(dbm.database_name)
    form_model_docs = dbm.load_all_rows_in_view('all_questionnaire', key=form_code, stale='ok')
    return form_model_docs

def _get_form_model_docs(dbm, form_code):
    cache_manger = get_cache_manager()
    cache_key = get_form_model_cache_key(form_code, dbm)
    form_model_docs = cache_manger.get(cache_key)
    if form_model_docs:
        return form_model_docs
    form_model_docs = _fetch_form_model_docs_from_couch(dbm, form_code)
    if form_model_docs:
        raw_form_model_docs = [doc['value'] for doc in form_model_docs]
        cache_manger.set(cache_key, raw_form_model_docs, time=FORM_MODEL_EXPIRY_TIME_IN_SEC)
        return raw_form_model_docs

    return None

def _get_form_models(dbm, form_code):
    form_model_docs = _get_form_model_docs(dbm, form_code)
    if form_model_docs:
        return [FormModel.new_from_doc(dbm, FormModelDocument.wrap(form_model_doc)) for form_model_doc in form_model_docs]
    return None

def _get_survey_responses(dbm):
    # extra_params = _set_stale_state_for_large_accounts(dbm.database_name)

    return dbm.database.iterview("survey_response_by_survey_response_id/survey_response_by_survey_response_id", 80000,
                                 stale='ok')


def _process_survey_response(survey_response_doc, dbm, logger):
    try:
        survey_response = SurveyResponse.new_from_doc(dbm=dbm, doc=SurveyResponse.__document_class__.wrap(
            survey_response_doc['value']))

        if 'form_code' not in survey_response._doc:
            logger.error("form_code not present in survey response:%s" % survey_response.uuid)
            return None
        form_code = survey_response._doc['form_code']
        form_models = _get_form_models(dbm, survey_response._doc['form_code'])

        if not form_models:
            logger.error("No Questionnaire found for survey response:%s with form_code: %s" %
                         survey_response.uuid, survey_response._doc['form_code'])
            return None

        elif len(form_models) > 1:
            form_models.sort(key=lambda form_model: form_model._doc.created, reverse=True)
            matching_form_model = _get_matching_form_model(survey_response.created, form_models)

            if matching_form_model:
                del survey_response._doc['form_code']
                survey_response.form_model_id = matching_form_model.id
                survey_response.save(process_post_update=False)
                return form_code

            else:
                logger.error(
                    "No Questionnaire found with matching date for survey response: %s and form_code:%s" % survey_response.uuid,
                    survey_response._doc['form_code'])
                return None

        elif len(form_models) == 1:
            del survey_response._doc['form_code']
            survey_response.form_model_id = form_models[0].id
            survey_response.save(process_post_update=False)
            return form_code

    except Exception as e:
        logger.exception("Exception for survey response:%s" % survey_response.uuid)
        return None


def _clear_form_models_from_cache(form_codes, dbm):
    cache_manger = get_cache_manager()
    keys = [get_form_model_cache_key(form_code, dbm) for form_code in form_codes if form_code]
    if keys:
        cache_manger.delete_multi(keys)


def make_survey_response_link_to_form_model_document_id(db_name):
    dbm = get_db_manager(db_name)
    logger = logging.getLogger(db_name)
    form_codes = Set()
    try:
        for survey_response_doc in _get_survey_responses(dbm):
            form_code = _process_survey_response(survey_response_doc, dbm, logger)
            form_codes.add(form_code)

        _clear_form_models_from_cache(form_codes, dbm)
    except Exception as e:
        logger.exception(db_name)
    mark_as_completed(db_name)

migrate(all_db_names(), make_survey_response_link_to_form_model_document_id, version=(13, 1, 2), threads=3)