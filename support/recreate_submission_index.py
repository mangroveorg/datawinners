from django.core.management import call_command
from datawinners.main.couchdb.utils import all_db_names
from datawinners.search.manage_index import populate_submission_index
from mangrove.datastore.documents import FormModelDocument
from datawinners.search import form_model_change_handler
from datawinners.main.database import get_db_manager


def create_index():
    databases_to_index = all_db_names()
    for database_name in databases_to_index:
        dbm = get_db_manager(database_name)
        for row in dbm.load_all_rows_in_view('questionnaire'):
            form_model_change_handler(FormModelDocument.wrap(row["value"]), dbm)
        populate_submission_index(dbm)


call_command("syncviews")
create_index()