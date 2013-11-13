import sys
from mangrove.contrib.registration import GLOBAL_REGISTRATION_FORM_CODE
from mangrove.utils.test_utils.database_utils import delete_and_create_form_model

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

from datawinners.main.database import get_db_manager
from datawinners.main.couchdb.utils import all_db_names

import logging
from migration.couch.utils import migrate, mark_start_of_migration


def migration_to_update_constraints_for_datasender_registration(db_name):
    logger = logging.getLogger(db_name)
    dbm = get_db_manager(db_name)
    try:
        mark_start_of_migration(db_name)
        delete_and_create_form_model(dbm, GLOBAL_REGISTRATION_FORM_CODE)
    except Exception as e:
        logger.exception("Failed datasender registration form creation for: %s with message %s" % (db_name, e.message))
    logger.info('Completed Migration')


migrate(all_db_names(), migration_to_update_constraints_for_datasender_registration, version=(9, 0, 5))
