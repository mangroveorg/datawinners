import logging
import datetime

import requests
from datawinners.main.couchdb.utils import all_db_names

from migration.couch.utils import migrate, mark_as_completed
from datawinners import settings

TIMEOUT_IN_SECONDS = 120 * 60
View_pah = "%s/_design/%s/_view/%s?limit=1"
views = ['by_short_codes', 'count_entity_type', 'datasender_by_mobile', 'entity_by_short_code']


def _get_response_for_view(db_name, view_name):
    return requests.get(settings.COUCH_DB_SERVER + "/" + (View_pah % (db_name, view_name, view_name)),
                        auth=settings.COUCHDBMAIN_CREDENTIALS, timeout=TIMEOUT_IN_SECONDS)


def warm_up_contact_related_views(db_name):
    logger = logging.getLogger(db_name)
    try:
        for view in views:
            start_time = datetime.datetime.now()
            response = _get_response_for_view(db_name, view)
            logger.error('%s status:%d' % (view, response.status_code))
            logger.error('%s:%s' % (view, response.text))
            logger.error(('%s time-taken:' + str(datetime.datetime.now() - start_time)) % view)

    except Exception as e:
        logger.exception(db_name)
    mark_as_completed(db_name)


migrate(all_db_names(), warm_up_contact_related_views, version=(22, 0, 4), threads=5)