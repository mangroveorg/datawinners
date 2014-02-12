import sys
from mangrove.errors.MangroveException import FormModelDoesNotExistsException, QuestionCodeAlreadyExistsException

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

from mangrove.form_model.field import TextField
from mangrove.form_model.validation import TextLengthConstraint
from datawinners.main.couchdb.utils import all_db_names
from migration.couch.utils import migrate, mark_as_completed
from mangrove.form_model.form_model import get_form_model_by_code, EMAIL_FIELD, REGISTRATION_FORM_CODE
import logging
from datawinners.main.database import get_db_manager


def migration_to_add_email_data_for_web_users_in_couch(db_name):
    logger = logging.getLogger(db_name)
    logger.info('Starting Migration')
    mark_as_completed(db_name)
    manager = get_db_manager(db_name)
    try:
        form_model = get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    except FormModelDoesNotExistsException as f:
        logger.warning(f.message)
        return
    email_type = get_or_create_data_dict(manager, name='Name', slug='name', primitive_type='string')

    email_field = TextField(name=EMAIL_FIELD, code=EMAIL_FIELD, label="What is the subject's email",
                      defaultValue="" ,
                      instruction="Enter email id", constraints=[TextLengthConstraint(max=50)], required=False)
    try:
        form_model.add_field(email_field)
        form_model.save()
        logger.info("Migrated registration form")
    except QuestionCodeAlreadyExistsException as e:
        logger.warning('email field is present' + e.message)
    except Exception as e:
        logger.exception(e.message)

migrate(all_db_names(), migration_to_add_email_data_for_web_users_in_couch, version=(9, 0, 1))