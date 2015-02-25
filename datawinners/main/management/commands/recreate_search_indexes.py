import logging
from django.core.management.base import BaseCommand
from datawinners.main.database import get_db_manager
from datawinners.search.index_utils import get_elasticsearch_handle
from datawinners.search.manage_index import create_all_mappings, create_all_indices
from datawinners.main.couchdb.utils import all_db_names

logging.basicConfig(filename='/var/log/datawinners/recreate_search_index.log', level=logging.DEBUG,
                        format="%(asctime)s | %(thread)d | %(levelname)s | %(name)s | %(message)s")

def recreate_index_for_db(database_name, es, logger):
    try:
        es.delete_index(database_name)
    except Exception as e:
        logger.info("Could not delete index " + str(e.message))
    response = es.create_index(database_name, settings={"number_of_shards": 1, "number_of_replicas": 0})
    logger.info('%s search index created : %s' % (database_name, response.get('ok')))
    dbm = get_db_manager(database_name)
    try:
        create_all_mappings(dbm)
        create_all_indices(dbm)
    except Exception as e:
        logger.error("recreate index failed for database %s for" %dbm.database_name)

class Command(BaseCommand):
    def handle(self, *args, **options):
        es = get_elasticsearch_handle()
        if len(args) > 0:
            databases_to_index = args[0:]
        else:
            databases_to_index = all_db_names()
        for database_name in databases_to_index:
            logger = logging.getLogger(database_name)
            recreate_index_for_db(database_name, es, logger)
            logger.info('Done')

        print 'Completed!'


if __name__ == '__main__':
    es = get_elasticsearch_handle()
    logger = logging.getLogger('hni_testorg_slx364903')
    dbm = get_db_manager('hni_testorg_slx364903')
    recreate_index_for_db('hni_testorg_slx364903', es, logger)