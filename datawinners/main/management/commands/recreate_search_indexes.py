from django.core.management.base import BaseCommand
import elasticutils
from datawinners.main.management.commands.utils import document_stores_to_process
from datawinners.settings import ELASTIC_SEARCH_URL


class Command(BaseCommand):
    def handle(self, *args, **options):
        es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
        es.delete_all_indexes()
        for database_name in document_stores_to_process(args):
            response = es.create_index(database_name, settings={"number_of_shards": 1, "number_of_replicas": 0})
            print '%s search index created : %s' % (database_name, response.get('ok'))
        print 'Done'
