import logging
from celery.task import current
from requests.packages import urllib3
from datawinners.main.database import get_db_manager
from datawinners.settings import ELASTIC_SEARCH_URL
from datawinners.tasks import app


@app.task(max_retries=3, throw=False)
def async_populate_submission_index(db_name, form_code):
    logger = logging.getLogger('datawinners.tasks')
    try:
        try:
            dbm = get_db_manager(db_name)
            from datawinners.search.manage_index import populate_submission_index

            populate_submission_index(dbm, form_code)
            _clear_index_cache(dbm)
        except Exception as e:
            current.retry(exc=e)
    except Exception as e:
        logger.exception('Failed for db: %s ,form code: %s' % (db_name, form_code))
        logger.exception(e)


def _clear_index_cache(dbm):
    # clears the field data cache (used for sorting and faceting) for the specified index
    http = urllib3.PoolManager()
    http.request('POST', '%s_cache/clear?field_data=true&index=%s' % (ELASTIC_SEARCH_URL, dbm.database_name))