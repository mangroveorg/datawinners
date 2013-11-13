import re
import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

from datawinners.main.database import get_db_manager
from mangrove.datastore.entity import get_all_entities
from datawinners.main.couchdb.utils import all_db_names

import logging
from migration.couch.utils import migrate, mark_start_of_migration


def migration_to_create_search_indxes_for_datasenders(db_name):
    logger = logging.getLogger(db_name)
    dbm = get_db_manager(db_name)
    all_ds = get_all_entities(dbm, ['reporter'])
    try:
        mark_start_of_migration(db_name)

        for ds in all_ds:
            if 'short_code' in ds.data.keys():
                short_code = ds.data['short_code']['value']
                if re.search('[A-Z]', short_code):
                    ds.data['short_code']['value'] = short_code.lower()
                    ds.save()
                    logger.info('Migrated short_code:%s' % short_code)
    except Exception as e:
        logger.exception("Failed DB: %s with message %s" % (db_name, e.message))
    logger.info('Completed Migration')


migrate(all_db_names(), migration_to_create_search_indxes_for_datasenders, version=(9, 0, 4))
