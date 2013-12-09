import sys
from datawinners.main.couchdb.utils import all_db_names
from datawinners.search.manage_index import populate_submission_index
from datawinners.search.submission_index import create_submission_mapping

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

import logging

from datawinners.search.index_utils import get_elasticsearch_handle
from datawinners.main.database import get_db_manager
from mangrove.form_model.form_model import FormModel
from mangrove.datastore.documents import FormModelDocument
from mangrove.errors.MangroveException import FormModelDoesNotExistsException
from migration.couch.utils import migrate, mark_start_of_migration


def create_submission_index(database_name):
    dbm = get_db_manager(database_name)
    for row in dbm.load_all_rows_in_view('questionnaire'):
        form_model = FormModel.new_from_doc(dbm, FormModelDocument.wrap(row["value"]))
        create_submission_mapping(dbm, form_model)

    populate_submission_index(dbm)


def create_search_indices_for_submissions(db_name):
    logger = logging.getLogger(db_name)
    try:
        mark_start_of_migration(db_name)
        logger.info('Starting indexing')
        create_submission_index(db_name)
        logger.info('Completed Indexing')

    except FormModelDoesNotExistsException as e:
        logger.warning(e.message)
    except Exception as e:
        logger.exception(e.message)


es = get_elasticsearch_handle()
migrate(all_db_names(), create_search_indices_for_submissions, version=(10, 0, 1), threads=1)


