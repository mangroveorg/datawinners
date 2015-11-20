import logging

from mangrove.datastore.documents import FormModelDocument
from datawinners.main.couchdb.utils import all_db_names
from datawinners.search import form_model_change_handler
from datawinners.main.database import get_db_manager
from migration.couch.utils import migrate, mark_as_completed

def update_mapping(database_name):
    try:
        dbm = get_db_manager(database_name)
        logger = logging.getLogger(database_name)

        for row in dbm.load_all_rows_in_view('questionnaire'):
            form_model_doc = FormModelDocument.wrap(row["value"])
            form_model_change_handler(form_model_doc, dbm)
    except Exception as e:
        logger.error(
            "Mapping update failed for database %s for form model %s " % (database_name, form_model_doc.form_code))
        logger.error(e)
    mark_as_completed(database_name)

migrate(all_db_names(), update_mapping, version=(27, 2, 1), threads=2)
