from django.core.management.base import BaseCommand
import elasticutils
from datawinners.main.database import get_db_manager
from datawinners.main.management.commands.utils import document_stores_to_process
from datawinners.search import subject_search_update, subject_model_change_handler
from datawinners.settings import ELASTIC_SEARCH_URL
from mangrove.datastore.documents import FormModelDocument
from mangrove.datastore.entity import get_all_entities


def update_subject_index(dbname):
    dbm = get_db_manager(dbname)
    for row in dbm.load_all_rows_in_view('questionnaire'):
        form_model_doc = FormModelDocument.wrap(row["value"])
        subject_model_change_handler(form_model_doc,dbm)
    for entity in get_all_entities(dbm):
        subject_search_update(entity, dbm)


class Command(BaseCommand):
    def handle(self, *args, **options):
        es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
        es.delete_all_indexes()
        for database_name in document_stores_to_process(args):
            response = es.create_index(database_name, settings={"number_of_shards": 1, "number_of_replicas": 0})
            print '%s search index created : %s' % (database_name, response.get('ok'))
            update_subject_index(database_name)
        print 'Done'
