import sys
from datawinners.search.index_utils import get_elasticsearch_handle
from datawinners.main.database import get_db_manager

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")
from datawinners.main.couchdb.utils import all_db_names

import logging
from migration.couch.utils import migrate, mark_start_of_migration
es = get_elasticsearch_handle()

def delete_submission_mapping(db_name):
    logger = logging.getLogger(db_name)
    try:
        mark_start_of_migration(db_name)
        logger.info('Starting migration')
        dbm = get_db_manager(db_name)
        rows = dbm.load_all_rows_in_view("questionnaire")
        for row in rows:
            index_name = dbm.database_name
            doc_type = row['value']['_id']
            try:
                es.send_request('DELETE', [index_name, doc_type, '_mapping'])
            except Exception as e:
                logging.error('Failed to delete mapping for index: %s and doctype: %s', index_name, doc_type)
                logging.error("exception %s", e)
                pass
    except Exception as e:
        logger.exception(e.message)

migrate(all_db_names(), delete_submission_mapping, version=(10, 0, 8), threads=1)
