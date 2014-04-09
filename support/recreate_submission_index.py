import logging

from django.core.management import call_command
from mangrove.datastore.documents import FormModelDocument, SurveyResponseDocument, ProjectDocument

from datawinners.main.couchdb.utils import all_db_names
from datawinners.project.models import Project
from datawinners.search.index_utils import get_elasticsearch_handle
from datawinners.search import form_model_change_handler
from datawinners.main.database import get_db_manager
from datawinners.search.submission_index import _update_with_form_model_fields, _meta_fields


logging.basicConfig(filename='/var/log/datawinners/migration_release_recreate_index.log', level=logging.DEBUG,
                    format="%(asctime)s | %(thread)d | %(levelname)s | %(name)s | %(message)s")


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
        logging.info('Created index for survey response docs ' + str([doc.get('id') for doc in survey_response_docs]))


def create_index():
    databases_to_index = all_db_names()
    for database_name in databases_to_index:
        try:
            dbm = get_db_manager(database_name)
            for row in dbm.load_all_rows_in_view('questionnaire'):
                form_model_doc = FormModelDocument.wrap(row["value"])
                form_model_change_handler(form_model_doc, dbm)
                try:
                    create_submission_index(dbm, row)
                except Exception as e:
                    logging.error("Index update failed for database %s and for formmodel %s" % (database_name, row.id))
                    logging.error(e)
        except Exception as e:
            logging.error(
                "Mapping update failed for database %s for form model %s " % (database_name, form_model_doc.form_code))
            logging.error(e)


try:
    call_command("syncviews", "syncall")
except Exception as e:
    logging.error("syncing views failed for one or more databases")
    logging.error(e)
create_index()
