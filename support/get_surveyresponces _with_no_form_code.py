import logging
from django.core.management import call_command
from datawinners.main.couchdb.utils import all_db_names
from datawinners.search.manage_index import populate_submission_index
from mangrove.datastore.documents import FormModelDocument
from datawinners.search import form_model_change_handler
from datawinners.main.database import get_db_manager


logging.basicConfig(filename='/var/log/datawinners/migration_survey_responses_without_form_code.log', level=logging.DEBUG,
                        format="%(asctime)s | %(thread)d | %(levelname)s | %(name)s | %(message)s")
invalid_surveyresponses = """
function(doc) {
    var isNull = function(o) {
        return ((o === undefined) || (o == null) || (o=="") || (o==" "));
    };
    if (doc.document_type == 'SurveyResponse' && isNull(doc.form_code)) {
        emit(doc._id,doc);
    }
}
"""

def check_survey_responses():
    databases_to_index = all_db_names()
    for database_name in databases_to_index:
        logging.info('Starting checking for database %s' %database_name)
        try:
            dbm = get_db_manager(database_name)
            rows = dbm.database.query(invalid_surveyresponses, include_docs=False)
            if len(rows)!=0:
                logging.debug("invalid survey_responses present for %s" % database_name)
        except Exception as e:
            logging.error(
                "retrival of survey responses failed for %s" % database_name)
            logging.error(e)

check_survey_responses()