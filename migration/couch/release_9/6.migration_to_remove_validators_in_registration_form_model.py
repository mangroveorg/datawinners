import sys
from mangrove.errors.MangroveException import FormModelDoesNotExistsException

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

from migration.couch.utils import mark_start_of_migration
from mangrove.form_model.form_model import get_form_model_by_code, REGISTRATION_FORM_CODE
import logging
from datawinners.main.database import get_db_manager


def migration_to_remove_validators_from_registration_form_model(db_name):
    logger = logging.getLogger(db_name)
    logger.info('Starting Migration')
    #mark_start_of_migration(db_name)
    manager = get_db_manager(db_name)
    try:
        form_model = get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    except FormModelDoesNotExistsException as f:
        logger.warning(f.message)
        return
    form_model.validators = []
    form_model.save()
    logger.info("Migrated registration form")

#migrate(all_db_names(), migration_to_remove_validators_from_registration_form_model, version=(9, 0, 6))
migration_to_remove_validators_from_registration_form_model('hni_testorg_slx364903')