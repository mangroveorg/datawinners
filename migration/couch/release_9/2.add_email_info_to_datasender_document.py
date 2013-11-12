import sys
from mangrove.errors.MangroveException import FormModelDoesNotExistsException, DataObjectAlreadyExists

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

from datawinners.accountmanagement.models import NGOUserProfile, OrganizationSetting
from datawinners.main.couchdb.utils import all_db_names
from mangrove.datastore.entity import get_by_short_code_include_voided
from mangrove.form_model.form_model import get_form_model_by_code, REGISTRATION_FORM_CODE
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE
import logging
from datawinners.main.database import get_db_manager
from migration.couch.utils import migrate, mark_start_of_migration


def add_email_data_to_entity_document(manager, short_code, data, logger):
    datasender = get_by_short_code_include_voided(manager, short_code, REPORTER_ENTITY_TYPE)
    if "email" not in datasender.data.keys():
        datasender.update_latest_data([data])
        logger.info('migrated: short_code: %s'%short_code)
    else:
        logger.info('Already migrated')

def migration_to_add_email_data_for_web_users_in_couch(db_name):
    logger = logging.getLogger(db_name)
    logger.info('Starting Migration')
    mark_start_of_migration(db_name)
    manager = get_db_manager(db_name)

    email_field_code = "email"
    try:
        form_model = get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    except FormModelDoesNotExistsException as f:
        logger.warning(f.message)
        return

    email_field_label = form_model._get_field_by_code(email_field_code).name
    email_ddtype = form_model._get_field_by_code(email_field_code).ddtype

    org_id = OrganizationSetting.objects.get(document_store=manager.database_name).organization_id
    user_profiles = NGOUserProfile.objects.filter(org_id=org_id)

    for user_profile in user_profiles:
        try:
            short_code = user_profile.reporter_id
            email_value = user_profile.user.email
            data = (email_field_label, email_value, email_ddtype)
            if short_code:
                add_email_data_to_entity_document(manager, short_code, data, logger)
        except DataObjectAlreadyExists as e:
            logger.warning(e.message)
        except Exception as e:
            logger.exception("FAILED to migrate: %s" %short_code)


migrate(all_db_names(), migration_to_add_email_data_for_web_users_in_couch, version=(9, 0, 2))