import logging
from django.core.management.base import BaseCommand
from datawinners.main.database import get_db_manager
from datawinners.search.index_utils import get_elasticsearch_handle
from datawinners.search.manage_index import create_all_mappings, create_all_indices, populate_submission_index
from datawinners.main.couchdb.utils import all_db_names
from datawinners.search.mapping import form_model_change_handler
from apscheduler.threadpool import ThreadPool
from mangrove.form_model.form_model import get_form_model_by_code
import time

threads = 2
logging.basicConfig(filename='/var/log/datawinners/recreate_search_index.log', level=logging.INFO,
                        format="%(asctime)s | %(thread)d | %(levelname)s | %(name)s | %(message)s")

def recreate_index_for_questionnaire(database_name, form_code):
    start = time.time()
    es = get_elasticsearch_handle()
    
    dbm = get_db_manager(database_name)
    try:
        form_model = get_form_model_by_code(dbm, form_code)
        create_mapping_for_form_model(dbm, form_model)
        populate_submission_index(dbm, form_model.id)
    except Exception as e:
        logger.exception("recreate index failed for database %s for" %dbm.database_name)

    logger.info('Time taken (seconds) for indexing {database_name} : {timetaken}'
                .format(database_name=database_name,timetaken=(time.time()-start)))

def create_mapping_for_form_model(dbm, form_model):
    form_model_change_handler(form_model._doc, dbm)


class DWThreadPool(ThreadPool):
    def submit(self, func, *args, **kwargs):
        def callback_wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as e:
                logging.exception(e.message)
            self._queue.task_done()

        return super(DWThreadPool, self).submit(callback_wrapper, *args, **kwargs)

    def wait_for_completion(self):
        self._queue.join()


class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args) == 2 :
            db_name, form_code = args[0], args[1]
        else:
            print "Not enough arguments!!!"
            return

        pool = DWThreadPool(threads, threads)
        pool.submit(recreate_index_for_questionnaire, db_name, form_code)

        pool.wait_for_completion()

        print 'Completed!'


if __name__ == '__main__':
    es = get_elasticsearch_handle()
    db_name = 'hni_testorg_slx364903'
    logger = logging.getLogger(db_name)
    dbm = get_db_manager(db_name)
    recreate_index_for_questionnaire("hni_marie-stopes-int-cambodia_ejn610045", "108")#, es, logger)

