import logging

import requests

from migration.couch.utils import migrate, mark_as_completed
from datawinners import settings

TIMEOUT_IN_SECONDS = 120 * 60

LARGE_ACCOUNTS = ['hni_palme_flm546389', 'hni_usaid-mikolo_lei526034', 'hni_psi_dmf792011']


def _get_response_for_view(db_name, view_name):
    return requests.get(settings.COUCH_DB_SERVER + "/" + (view_name % db_name),
                        auth=settings.COUCHDBMAIN_CREDENTIALS, timeout=TIMEOUT_IN_SECONDS)


def warm_up_views_for_large_accounts(db_name):
    logger = logging.getLogger(db_name)
    try:
        survey_response_view = "%s/_design/survey_response_by_survey_response_id/_view/survey_response_by_survey_response_id?limit=1"
        response = _get_response_for_view(db_name, survey_response_view)
        logger.error('%s: survey_response status:%d' % (db_name, response.status_code))
        logger.error('%s: survey_response:%s' % (db_name, response.text))

        all_questionnaire_view = "%s/_design/all_questionnaire/_view/all_questionnaire?limit=1"
        response = _get_response_for_view(db_name, all_questionnaire_view)
        logger.error('%s: all_questionnaire_view status:%d' % (db_name, response.status_code))
        logger.error('%s: all_questionnaire:%s' % (db_name, response.text))
    except Exception as e:
        logger.exception(db_name)
    mark_as_completed(db_name)


migrate(LARGE_ACCOUNTS, warm_up_views_for_large_accounts, version=(13, 1, 1), threads=3)