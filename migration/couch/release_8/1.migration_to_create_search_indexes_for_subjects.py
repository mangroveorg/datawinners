import sys
from datawinners.search.index_utils import get_elasticsearch_handle

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.management.commands.recreate_search_indexes import recreate_index_for_db

import logging
from migration.couch.utils import migrate, mark_as_completed


def create_search_indices_for_subjects(db_name):
    logger = logging.getLogger(db_name)
    try:
        mark_as_completed(db_name)
        logger.info('Starting indexing')
        recreate_index_for_db(db_name, es)
    except Exception as e:
        logger.exception("Failed DB: %s with message %s" % (db_name, e.message))
    logger.info('Completed Indexing')


es = get_elasticsearch_handle()
migrate(all_db_names(), create_search_indices_for_subjects, version=(8, 0, 1), threads=1)
