import sys
from datawinners.main.database import get_db_manager
from datawinners.search import entity_search_update
from datawinners.search.index_utils import get_elasticsearch_handle
from mangrove.datastore.entity import get_all_entities, get_all_entities_include_voided
from mangrove.errors.MangroveException import FormModelDoesNotExistsException
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")
from datawinners.main.couchdb.utils import all_db_names

import logging
from migration.couch.utils import migrate, mark_start_of_migration


def create_search_indices_for_datasenders(db_name):
    logger = logging.getLogger(db_name)
    try:
        mark_start_of_migration(db_name)
        logger.info('Starting indexing')
        dbm = get_db_manager(db_name)

        for entity in get_all_entities_include_voided(dbm):
            if entity.is_void():
                entity_search_update(entity,dbm)

        logger.info('Completed Indexing')

    except FormModelDoesNotExistsException as e:
        logger.warning(e.message)
    except Exception as e:
        logger.exception(e.message)


es = get_elasticsearch_handle()
migrate(all_db_names(), create_search_indices_for_datasenders, version=(9, 0, 7), threads=1)
