import logging
from mangrove.contrib.registration import GLOBAL_REGISTRATION_FORM_CODE
from mangrove.utils.test_utils.database_utils import delete_and_create_form_model
from datawinners.main.database import get_db_manager
from datawinners.main.couchdb.utils import all_db_names
from migration.couch.utils import migrate, mark_as_completed


def migration_to_update_constraints_for_datasender_registration(db_name):
    logger = logging.getLogger(db_name)
    dbm = get_db_manager(db_name)
    try:
        delete_and_create_form_model(dbm, GLOBAL_REGISTRATION_FORM_CODE)
        mark_as_completed(db_name)
    except Exception as e:
        logger.exception("Datasender registration form re-creation failed for: %s with message %s" % (db_name, e.message))
    logger.info('Completed Migration')


migrate(all_db_names(), migration_to_update_constraints_for_datasender_registration, version=(10, 1, 2), threads=2)
