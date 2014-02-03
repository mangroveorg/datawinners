import sys
from datawinners.search.index_utils import get_elasticsearch_handle
from mangrove.errors.MangroveException import FormModelDoesNotExistsException

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")
from datawinners.main.couchdb.utils import all_db_names
from datawinners.search.datasender_index import create_datasender_index

import logging
from migration.couch.utils import migrate, mark_as_completed


def create_search_indices_for_datasenders(db_name):
    logger = logging.getLogger(db_name)
    try:
        mark_as_completed(db_name)
        logger.info('Starting indexing')
        create_datasender_index(db_name)
        logger.info('Completed Indexing')

    except FormModelDoesNotExistsException as e:
        logger.warning(e.message)
    except Exception as e:
        logger.exception(e.message)


es = get_elasticsearch_handle()
migrate(all_db_names(), create_search_indices_for_datasenders, version=(9, 0, 7), threads=1)
