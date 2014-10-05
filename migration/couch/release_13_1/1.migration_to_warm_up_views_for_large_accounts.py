import logging
import datetime

import requests
from datawinners.main.couchdb.utils import all_db_names

from migration.couch.utils import migrate, mark_as_completed
from datawinners import settings

TIMEOUT_IN_SECONDS = 120 * 60

# LARGE_ACCOUNTS = ['hni_palme_flm546389', 'hni_usaid-mikolo_lei526034', 'hni_psi_dmf792011']


def _get_response_for_view(db_name, view_name):
    return requests.get(settings.COUCH_DB_SERVER + "/" + (view_name % db_name),
                        auth=settings.COUCHDBMAIN_CREDENTIALS, timeout=TIMEOUT_IN_SECONDS)


def warm_up_views_for_large_accounts(db_name):
    logger = logging.getLogger(db_name)
    try:
        start_time = datetime.datetime.now()
        survey_response_view = "%s/_design/survey_response_by_survey_response_id/_view/survey_response_by_survey_response_id?limit=1"
        response = _get_response_for_view(db_name, survey_response_view)
        logger.error('survey_response status:%d' % response.status_code)
        logger.error('survey_response:%s' % response.text)
        logger.error('survey_response time-taken:' + str(datetime.datetime.now()-start_time))

        start_time = datetime.datetime.now()
        all_questionnaire_view = "%s/_design/all_questionnaire/_view/all_questionnaire?limit=1"
        response = _get_response_for_view(db_name, all_questionnaire_view)
        logger.error('all_questionnaire_view status:%d' % response.status_code)
        logger.error('all_questionnaire:%s' % response.text)
        logger.error('all_questionnaire time-taken:' + str(datetime.datetime.now()-start_time))

    except Exception as e:
        logger.exception(db_name)
    mark_as_completed(db_name)


migrate(all_db_names(), warm_up_views_for_large_accounts, version=(13, 1, 1), threads=5)