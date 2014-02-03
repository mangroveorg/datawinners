import sys
from datawinners.main.couchdb.utils import all_db_names

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0,".")

from migration.couch.utils import should_not_skip, mark_as_completed, init_migrations
from datetime import datetime
import traceback
from mangrove.datastore.database import get_db_manager
from mangrove.transport.contract.survey_response import SurveyResponse

SERVER = 'http://localhost:5984'
log_file = open('/var/log/datawinners/migration_release_6_1_2.log', 'a')
init_migrations('/var/log/datawinners/dbs_migrated_release_6_1_2.csv')

map_invalid_survey_responses = """
function(doc){
    if(doc.document_type == 'SurveyResponse' && doc.data_record_id == null && doc.values == null && !doc.void)
        emit(null, doc);
}"""

def migrate_db(database):
    mark_as_completed(database)
    log_statement('\nStart migration on database : %s \n' % database)
    try:
        manager = get_db_manager(server=SERVER, database=database)
        invalid_survey_response_docs = manager.database.query(map_invalid_survey_responses)
        count = 0
        log_statement('Total documents to be voided : %s' % len(invalid_survey_response_docs))
        for survey_response_doc in invalid_survey_response_docs:
            survey_response = SurveyResponse.new_from_doc(dbm=manager,
                doc=SurveyResponse.__document_class__.wrap(survey_response_doc['value']))
            survey_response.void()
            count += 1
            log_statement("Voided survey_response %s" % survey_response.uuid)
        log_statement("Total number of documents voided are %s" % count)
        log_statement('\nCompleted database : %s\n' % database)
    except Exception as e:
        log_statement('error:%s\n' % database)
        traceback.print_exc(file=log_file)


def migrate_bug_2134(all_db_names):
    print "start ...."
    for database in all_db_names:
        if should_not_skip(database):
            print "starting database : %s" % database
            log_statement('\nStart ==============================================================================\n')
            migrate_db(database)
            log_statement('\n End ================================================================================\n')

    print "Completed migration"

def log_statement(statement):
    log_file.writelines('%s : %s\n' % (datetime.utcnow(), statement))

migrate_bug_2134(all_db_names(SERVER))
