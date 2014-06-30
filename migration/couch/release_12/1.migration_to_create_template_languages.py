import logging
from datawinners.common.lang.messages import CustomizedMessage, ACCOUNT_MESSAGE_DOC_ID
from datawinners.common.lang.utils import create_custom_message_templates
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from migration.couch.utils import migrate, mark_as_completed


def create_language_template(dbm, logger):
    create_custom_message_templates(dbm)


def delete_existing_templates(dbm):
    customized_message_rows = dbm.load_all_rows_in_view('all_languages', include_docs=True)
    for row in customized_message_rows:
        dbm.database.delete(row.doc)
    account_message = dbm.database.get(ACCOUNT_MESSAGE_DOC_ID)
    if account_message:
        dbm.database.delete(account_message)



def migrate_to_create_language_templates(db_name):
    logger = logging.getLogger(db_name)
    try:
        logger.info('Starting migration')
        dbm = get_db_manager(db_name)
        delete_existing_templates(dbm)
        create_language_template(dbm, logger)
    except Exception as e:
        logger.exception(e.message)
    mark_as_completed(db_name)


migrate(all_db_names(), migrate_to_create_language_templates, version=(12, 0, 1), threads=3)