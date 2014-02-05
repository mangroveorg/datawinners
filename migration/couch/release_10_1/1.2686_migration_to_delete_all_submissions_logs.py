import logging
from datawinners.main.database import get_db_manager
from datawinners.main.couchdb.utils import all_db_names
from migration.couch.utils import migrate, mark_as_completed

list_all_submission_logs = """
function(doc) {
    var isNotNull = function(o) {
        return !((o === undefined) || (o == null));
    };
    if (doc.document_type == 'SubmissionLog') {
        emit(doc._id, null);
    }
}"""


def delete_all_submission_logs(db_name):
    logger = logging.getLogger(db_name)
    try:
        logger.info('Starting migration')
        dbm = get_db_manager(db_name)
        for row in dbm.database.query(list_all_submission_logs, include_docs = True):
            try:
                dbm.database.delete(row.doc)
            except Exception as e:
                logging.error('Deletion failed for database : %s, doc with id: %s', db_name, row['value']['_id'])
                logging.error(e)
        mark_as_completed(db_name)
    except Exception as e:
        logger.exception(e.message)


migrate(all_db_names(), delete_all_submission_logs, version=(10, 1, 1), threads=1)