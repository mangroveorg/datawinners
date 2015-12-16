import logging
import time
from celery.task import current
from requests.packages import urllib3
from datawinners.main.database import get_db_manager
from datawinners.settings import ELASTIC_SEARCH_URL
from datawinners.tasks import app
from mangrove.form_model.form_model import FormModel
from datawinners.search.submission_index import SubmissionSearchStore


@app.task(max_retries=3, throw=False)
def async_populate_submission_index(db_name, form_model_id):
    _populate_submission_index(db_name, form_model_id)
    
@app.task(max_retries=1, throw=False, track_started=True)
def async_reindex(db_name, form_model_id):
    response = dict()
    response['db_name'] = db_name
    response['questionnaire_id'] = form_model_id
    response['start_time'] = time.time()
    dbm = get_db_manager(db_name)
    form_model = FormModel.get(dbm, form_model_id)
    submission_search_store = SubmissionSearchStore(dbm, form_model, old_form_model=None)
    submission_search_store.recreate_elastic_store()
    _populate_submission_index(db_name, form_model_id)
    response['end_time'] = time.time()
    return response
    
def _populate_submission_index(db_name, form_model_id):
    logger = logging.getLogger('datawinners.tasks')
    try:
        try:
            dbm = get_db_manager(db_name)
            from datawinners.search.manage_index import populate_submission_index

            populate_submission_index(dbm, form_model_id)
            _clear_index_cache(dbm)
        except Exception as e:
            current.retry(exc=e)
    except Exception as e:
        logger.exception('Failed for db: %s ,form model id: %s' % (db_name, form_model_id))
        logger.exception(e)

def _clear_index_cache(dbm):
    # clears the field data cache (used for sorting and faceting) for the specified index
    http = urllib3.PoolManager()
    http.request('POST', '%s_cache/clear?field_data=true&index=%s' % (ELASTIC_SEARCH_URL, dbm.database_name))