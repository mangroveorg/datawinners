import logging
from django.core.management.base import BaseCommand
import elasticutils
from datawinners.feeds.database import get_feed_db_from_main_db_name
from datawinners.main.database import get_db_manager
from mangrove.datastore.documents import FormModelDocument, EnrichedSurveyResponseDocument
from datawinners.main.couchdb.utils import all_db_names
from datawinners.search import form_model_change_handler, entity_search_update, update_submission_search_index
from datawinners.settings import ELASTIC_SEARCH_URL, ELASTIC_SEARCH_TIMEOUT
from mangrove.datastore.entity import Entity


def _create_mappings(dbm):
    for row in dbm.load_all_rows_in_view('questionnaire'):
        form_model_doc = FormModelDocument.wrap(row["value"])
        form_model_change_handler(form_model_doc, dbm)


def _populate_entity_index(dbm):
    rows = dbm.database.iterview('by_short_codes/by_short_codes', 100, reduce=False, include_docs=True)
    for row in rows:
        entity = Entity.__document_class__.wrap(row.get('doc'))
        entity_search_update(entity, dbm)


def _populate_submission_index(dbm):
    feeds_dbm = get_feed_db_from_main_db_name(dbm.database_name)
    rows = dbm.database.iterview("surveyresponse/surveyresponse", 1000,reduce=False,include_docs=False)
    for row in rows:
        enriched_survey_response = feeds_dbm._load_document(row.get('id'), EnrichedSurveyResponseDocument)
        if enriched_survey_response is not None:
            update_submission_search_index(enriched_survey_response,feeds_dbm)

def _create_indices(dbm):
    _populate_entity_index(dbm)
    _populate_submission_index(dbm)


def recreate_index_for_db(database_name, es):
    try:
        es.delete_index(database_name)
    except Exception as e:
        logging.info("Could not delete index " + e.message)
    response = es.create_index(database_name, settings={"number_of_shards": 1, "number_of_replicas": 0})
    logging.info('%s search index created : %s' % (database_name, response.get('ok')))
    dbm = get_db_manager(database_name)
    _create_mappings(dbm)
    _create_indices(dbm)

class Command(BaseCommand):
    def handle(self, *args, **options):
        es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT)
        if len(args) > 0:
            databases_to_index = args[0:]
        else:
            databases_to_index = all_db_names()
        for database_name in databases_to_index:
            recreate_index_for_db(database_name, es)
            print 'Done' + database_name

        print 'Completed!'

es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT)
databases_to_index = all_db_names()
for database_name in databases_to_index:
    recreate_index_for_db(database_name, es)
