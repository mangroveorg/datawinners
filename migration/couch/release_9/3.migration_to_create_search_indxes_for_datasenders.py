import sys
from mangrove.errors.MangroveException import FormModelDoesNotExistsException

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")
import elasticutils
from datawinners.main.couchdb.utils import all_db_names
from datawinners.settings import ELASTIC_SEARCH_URL
from datawinners.search.datasender_index import create_datasender_index

import logging
from migration.couch.utils import migrate, mark_start_of_migration


def create_search_indices_for_datasenders(db_name):
    logger = logging.getLogger(db_name)
    try:
        mark_start_of_migration(db_name)
        logger.info('Starting indexing')
        create_datasender_index(db_name)

    except FormModelDoesNotExistsException as e:
        logger.warning(e.message)
    except Exception as e:
        logger.exception(e.message)
    logger.info('Completed Indexing')


es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL, timeout=180)
migrate(all_db_names(), create_search_indices_for_datasenders, version=(9, 0, 3), threads=1)
