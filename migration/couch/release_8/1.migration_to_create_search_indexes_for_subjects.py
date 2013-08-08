import sys
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")
import elasticutils
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.management.commands.recreate_search_indexes import recreate_index_for_db
from datawinners.settings import ELASTIC_SEARCH_URL


import logging
from migration.couch.utils import migrate, mark_start_of_migration


def create_search_indices_for_subjects(db_name):
    logger = logging.getLogger(db_name)
    try:
        mark_start_of_migration(db_name)
        logger.info('Starting indexing')
        recreate_index_for_db(db_name, es)
    except Exception as e:
        logger.exception("Failed DB: %s with message %s" % (db_name, e.message))
    logger.info('Completed Indexing')

es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
migrate(all_db_names    (), create_search_indices_for_subjects, version=(8, 0, 1))