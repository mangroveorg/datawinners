import logging
from django.core.management import call_command
from datawinners.main.couchdb.utils import all_db_names
from datawinners.search.manage_index import populate_submission_index
from mangrove.datastore.documents import FormModelDocument
from datawinners.search import form_model_change_handler
from datawinners.main.database import get_db_manager


logging.basicConfig(filename='/var/log/datawinners/migration_survey_responces_without_form_code.log', level=logging.DEBUG,
                        format="%(asctime)s | %(thread)d | %(levelname)s | %(name)s | %(message)s")
map_invalid_surveyresponces = """
function(doc) {
    var isNull = function(o) {
        return ((o === undefined) || (o == null) || (o=="") || (o==" "));
    };
    if (doc.document_type == 'SurveyResponse' && isNull(doc.form_code)) {
        emit(doc._id,doc);
    }
}
"""

def check_survey_responces():
    databases_to_index = all_db_names()
    for database_name in databases_to_index:
        try:
            dbm = get_db_manager(database_name)
            rows=dbm.load_all_rows_in_view('invalid_surveyresponces')
            if len(rows)!=0:
                logging.debug("invalid survey_responces present for %s" % database_name)
        except Exception as e:
            logging.error(
                "retrival of survey responces failed for %s" % database_name)
            logging.error(e)

check_survey_responces()