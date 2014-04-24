import logging

from mangrove.datastore.documents import FormModelDocument, SurveyResponseDocument, ProjectDocument

from datawinners.main.couchdb.utils import all_db_names
from datawinners.project.models import Project
from datawinners.search.index_utils import get_elasticsearch_handle
from datawinners.search import form_model_change_handler
from datawinners.main.database import get_db_manager
from datawinners.search.submission_index import _update_with_form_model_fields, _meta_fields
from migration.couch.utils import migrate, mark_as_completed


def create_submission_index(dbm, row):
    form_model = Project.new_from_doc(dbm, ProjectDocument.wrap(row["value"]))
    form_code = form_model.form_code
    start_key = [form_code]
    end_key = [form_code, {}]
    rows = dbm.database.iterview("surveyresponse/surveyresponse", 1000, reduce=False, include_docs=False,
                                 startkey=start_key, endkey=end_key)
    es = get_elasticsearch_handle(timeout=600)

    survey_response_docs = []
    for row in rows:
        survey_response = SurveyResponseDocument._wrap_row(row)
        search_dict = _meta_fields(survey_response, dbm)
        _update_with_form_model_fields(dbm, survey_response, search_dict, form_model)
        search_dict.update({'id': survey_response.id})
        survey_response_docs.append(search_dict)

    if survey_response_docs:
        es.bulk_index(dbm.database_name, form_model.id, survey_response_docs)


def create_index(database_name):
    try:
        dbm = get_db_manager(database_name)
        logger = logging.getLogger(database_name)

        for row in dbm.load_all_rows_in_view('questionnaire'):
            form_model_doc = FormModelDocument.wrap(row["value"])
            form_model_change_handler(form_model_doc, dbm)
            try:
                create_submission_index(dbm, row)
                mark_as_completed(database_name)
            except Exception as e:
                logger.error("Index update failed for database %s and for formmodel %s" % (database_name, row.id))
                logger.error(e)
    except Exception as e:
        logger.error(
            "Mapping update failed for database %s for form model %s " % (database_name, form_model_doc.form_code))
        logger.error(e)

migrate(all_db_names(), create_index, version=(11, 0, 6), threads=2)
