import logging
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from mangrove.datastore.entity import Entity
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport.contract.survey_response import SurveyResponse
from migration.couch.utils import migrate


def _get_survey_responses_with_no_eid(dbm, logger):
    rows = dbm.database.view("surveyresponse/surveyresponse", reduce=False)
    inconsistent_survey_response_list = []
    for row in rows:
        try:
            survey_response = SurveyResponse.get(dbm, row.id)
            form_model = get_form_model_by_code(dbm, survey_response.form_code)
            if form_model.entity_defaults_to_reporter() and "eid" not in survey_response.values.keys():
                inconsistent_survey_response_list.append(survey_response)
        except Exception as e:
            logger.exception(e)
    return inconsistent_survey_response_list


def add_eid_field_for_survey_response_with_missing_eid_field(db_name):
    logger = logging.getLogger(db_name)
    logger.info('Starting Migration')
    dbm = get_db_manager(db_name)

    inconsistent_survey_response_list = _get_survey_responses_with_no_eid(dbm, logger)
    for survey_response in inconsistent_survey_response_list:
        if survey_response.owner_uid:
            data_sender = Entity.get(dbm, survey_response.owner_uid)
            survey_response.values['eid'] = data_sender.short_code
            logger.info("Migrated survey response: %s" % survey_response.uuid)
        else:
            logger.warning("Missing owner id for survey_response: %s, form_code: %s" % (
                survey_response.uuid, survey_response.form_code))
        logger.info("Number of survey responses migrated: %s" % len(inconsistent_survey_response_list))

migrate(all_db_names(), add_eid_field_for_survey_response_with_missing_eid_field, version=(8, 0, 3))