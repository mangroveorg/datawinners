import logging
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from mangrove.utils.dates import js_datestring_to_py_datetime
from migration.couch.utils import migrate, mark_as_completed


def find_deleted_questionnaires(db_name):
    dbm = get_db_manager(db_name)
    logger = logging.getLogger(db_name)
    questionnaires = dbm.load_all_rows_in_view('all_questionnaire')
    for questionnaire in questionnaires:
        if questionnaire['value']['void'] and questionnaire['value']['created'].year < 2014:
            questionnaire_value_id = questionnaire['value']['_id']
            logger.error("Deleted Questionnaire : %s" % questionnaire_value_id)
            rows = dbm.load_all_rows_in_view('surveyresponse', reduce=True, start_key=[questionnaire_value_id],
                                             end_key=[questionnaire_value_id, {}])
            if rows and len(rows) >= 1 and 'count' in rows[0]['value']:
                logger.error("Submission count : %d" % rows[0]['value']['count'])


    mark_as_completed(db_name)


migrate(all_db_names(), find_deleted_questionnaires, version=(14, 0, 3), threads=1)