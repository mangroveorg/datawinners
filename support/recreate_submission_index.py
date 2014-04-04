import logging
from django.core.management import call_command
from datawinners.main.couchdb.utils import all_db_names
from datawinners.search.manage_index import populate_submission_index
from mangrove.datastore.documents import FormModelDocument
from datawinners.search import form_model_change_handler
from datawinners.main.database import get_db_manager


logging.basicConfig(filename='/var/log/datawinners/migration_release_recreate_index.log', level=logging.DEBUG,
                        format="%(asctime)s | %(thread)d | %(levelname)s | %(name)s | %(message)s")

def create_index():
    databases_to_index = all_db_names()
    for database_name in databases_to_index:
        try:
            dbm = get_db_manager(database_name)
            for row in dbm.load_all_rows_in_view('questionnaire'):
                form_model_doc = FormModelDocument.wrap(row["value"])
                form_model_change_handler(form_model_doc, dbm)
            try:
                populate_submission_index(dbm)
            except Exception as e:
                logging.error("Index update failed for database %s" % database_name)
                logging.error(e)
        except Exception as e:
            logging.error(
                "Mapping update failed for database %s for form model %s " % (database_name, form_model_doc.form_code))
            logging.error(e)


call_command("syncviews")
create_index()