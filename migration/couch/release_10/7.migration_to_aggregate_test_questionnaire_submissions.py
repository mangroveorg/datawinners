import sys
from datawinners.main.database import get_db_manager

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")
from datawinners.main.couchdb.utils import all_db_names

import logging
from migration.couch.utils import migrate, mark_start_of_migration


def aggregate_test_questionnaire(dbm):
    survey_responses = dbm.load_all_rows_in_view("surveyresponse", reduce=False, include_doc=True)
    test_questionnaire_count_for_project_in_test_mode = 0
    test_questionnaire_count_for_project_in_active_mode = 0
    for survey_response in survey_responses:
        if survey_response['value']['created_by'] == 'test':
            if survey_response['value']['test']:
                test_questionnaire_count_for_project_in_test_mode += 1
            else:
                test_questionnaire_count_for_project_in_active_mode += 1
    logging.info("DatabaseName:%s\n", dbm.database_name)
    logging.info("Test Questionnaire count for project in test mode: %d\nTest Questionnaire count for project in active mode:%d",
        test_questionnaire_count_for_project_in_test_mode, test_questionnaire_count_for_project_in_active_mode)


def aggregate_test_questionnaire_submissions(db_name):
    logger = logging.getLogger(db_name)
    try:
        mark_start_of_migration(db_name)
        dbm = get_db_manager(db_name)
        aggregate_test_questionnaire(dbm)
    except Exception as e:
        logger.exception(e.message)


migrate(all_db_names(), aggregate_test_questionnaire_submissions, version=(10, 0, 7), threads=1)