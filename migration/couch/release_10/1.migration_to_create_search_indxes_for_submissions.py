import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

import logging

import elasticutils

from datawinners.feeds.database import get_feed_db_from_main_db_name
from datawinners.main.database import get_db_manager
from mangrove.form_model.form_model import FormModel
from mangrove.datastore.documents import FormModelDocument, EnrichedSurveyResponseDocument
from datawinners.search import create_submission_mapping, update_submission_search_index
from mangrove.errors.MangroveException import FormModelDoesNotExistsException
from datawinners.main.couchdb.utils import all_db_names
from datawinners.settings import ELASTIC_SEARCH_URL
from migration.couch.utils import migrate, mark_start_of_migration


def create_submission_index(database_name):
    dbm = get_db_manager(database_name)
    feeds_dbm = get_feed_db_from_main_db_name(database_name)
    for row in dbm.load_all_rows_in_view('questionnaire'):
        form_model = FormModel.new_from_doc(dbm, FormModelDocument.wrap(row["value"]))
        if not form_model.is_entity_registration_form():
            create_submission_mapping(dbm, form_model)

    rows = dbm.database.iterview("surveyresponse/surveyresponse",1000,reduce=False,include_docs=False)
    for row in rows:
        enriched_survey_response = feeds_dbm._load_document(row.get('id'), EnrichedSurveyResponseDocument)
        if enriched_survey_response is not None:
            update_submission_search_index(enriched_survey_response,feeds_dbm, refresh_index=False)

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


es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL, timeout=180)
migrate(all_db_names(), create_search_indices_for_submissions, version=(10, 0, 1), threads=1)


