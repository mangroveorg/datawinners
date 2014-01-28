import sys
from mangrove.errors.MangroveException import FormModelDoesNotExistsException

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

import logging
from datawinners.main.couchdb.utils import all_db_names
from datawinners.search.submission_index import create_submission_mapping, _meta_fields, _update_with_form_model_fields
from datawinners.search.index_utils import get_elasticsearch_handle
from datawinners.main.database import get_db_manager
from mangrove.form_model.form_model import FormModel
from mangrove.datastore.documents import FormModelDocument, SurveyResponseDocument
from migration.couch.utils import migrate, mark_start_of_migration


def create_index(dbm, form_model):
    form_code = form_model.form_code
    start_key = [form_code]
    end_key = [form_code, {}]
    rows = dbm.database.iterview("surveyresponse/surveyresponse", 1000, reduce=False, include_docs=False,
                                 startkey=start_key, endkey=end_key)
    es = get_elasticsearch_handle()
    es.delete_all(dbm.database_name, form_model.id)
    survey_response_docs = []
    for row in rows:
        survey_response = SurveyResponseDocument._wrap_row(row)
        search_dict = _meta_fields(survey_response, dbm)
        _update_with_form_model_fields(dbm, survey_response, search_dict, form_model)
        survey_response.update({'id': survey_response.uuid})
        survey_response_docs.append(survey_response)

    es.bulk_index(dbm.database_name, form_model.id, survey_response_docs)


def create_submission_index(database_name, logger):
    dbm = get_db_manager(database_name)
    for row in dbm.load_all_rows_in_view('questionnaire'):
        try:
            form_model = FormModel.new_from_doc(dbm, FormModelDocument.wrap(row["value"]))
        except FormModelDoesNotExistsException as e:
            logger.exception(e.message)
            continue
        if form_model.is_entity_registration_form() or "delete" == form_model.form_code:
            continue
        create_submission_mapping(dbm, form_model)
        create_index(dbm, form_model)


def create_search_indices_for_submissions(db_name):
    logger = logging.getLogger(db_name)
    try:
        mark_start_of_migration(db_name)
        logger.info('Starting indexing')
        create_submission_index(db_name, logger)
        logger.info('Completed Indexing')
    except Exception as e:
        logger.exception(e.message)


es = get_elasticsearch_handle()
migrate(all_db_names(), create_search_indices_for_submissions, version=(10, 0, 1), threads=1)


