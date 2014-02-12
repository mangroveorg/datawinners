import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

#noinspection PyUnresolvedReferences - used to initialize post save handlers for elasticsearch
import datawinners.search
from mangrove.datastore.entity import get_all_entities
from datawinners.main.database import get_db_manager
from datawinners.main.couchdb.utils import all_db_names

import logging
from migration.couch.utils import migrate, mark_as_completed


def _add_location_field_if_absent(datasender, dbm, logger):
    if "location" not in datasender.data and '_geo' in datasender.aggregation_paths.keys():
        logger.info('Adding location field to datasender %s' % datasender.short_code)
        data = ("location", datasender.aggregation_paths["_geo"], get_datadict_type_by_slug(dbm, slug='location'))
        datasender.update_latest_data([data])
    else:
        logger.info('Location field already present for datasender %s' % datasender.short_code)

def migration_to_add_location_field_to_datasenders(db_name):
    logger = logging.getLogger(db_name)
    dbm = get_db_manager(db_name)
    mark_as_completed(db_name)
    logger.info('Migration started for database %s' % db_name)
    all_ds = get_all_entities(dbm, ['reporter'])
    for ds in all_ds:
        _add_location_field_if_absent(ds, dbm, logger)

migrate(all_db_names(), migration_to_add_location_field_to_datasenders, version=(9, 0, 6))
