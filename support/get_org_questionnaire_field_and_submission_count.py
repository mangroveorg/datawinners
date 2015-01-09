import logging
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager

logging.basicConfig(filename='/var/log/datawinners/script_to_get_count', level=logging.DEBUG,
                        format="%(message)s")
def get_count(dbm, logger):
    db_name = dbm.database_name
    questionnaires = dbm.load_all_rows_in_view('all_questionnaire')
    for questionnaire in questionnaires:
        try:
            if not questionnaire['value']['void']:
                field_count = len(questionnaire.value["json_fields"])
                questionnaire_id = questionnaire.value['_id']
                questionnaire_name =questionnaire.value['name']
                rows = dbm.load_all_rows_in_view('surveyresponse', reduce=True, start_key=[questionnaire_id],
                                                 end_key=[questionnaire_id, {}])
                if rows and len(rows) >= 1 and 'count' in rows[0]['value']:
                    logger.info("organization - %s, questionnaire_id - %s, questionnaire-name-%s field_count - %dSubmission count : %d" % (
                    db_name, questionnaire_id, questionnaire_name, field_count, rows[0]['value']['count']))
        except Exception:
            logger.exception()


def get_counts_for(db_names):
    for db_name in db_names:
        dbm = get_db_manager(db_name)
        logger = logging.getLogger(db_name)
        get_count(dbm, logger)


get_counts_for(all_db_names())