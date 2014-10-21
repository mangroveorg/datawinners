import logging
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from migration.couch.utils import migrate, mark_as_completed


def advanced_questionnaire_usage(db_name):
    dbm = get_db_manager(db_name)
    logger = logging.getLogger(db_name)
    try:
        questionnaires = dbm.load_all_rows_in_view('all_projects')
        for questionnaire in questionnaires:
            if 'xform' in questionnaire['value'] and questionnaire['value']['xform']:
                questionnaire_id = questionnaire['value']['_id']
                rows = dbm.load_all_rows_in_view('surveyresponse', reduce=True, start_key=[questionnaire_id],
                                                 end_key=[questionnaire_id, {}])
                if rows and len(rows) >= 1 and 'count' in rows[0]['value']:
                    logger.error("Questionnaire: %s Submission count : %d" % (questionnaire_id, rows[0]['value']['count']))

    except Exception:
        logger.exception()
    mark_as_completed(db_name)


migrate(all_db_names(), advanced_questionnaire_usage, version=(14, 0, 2), threads=6)