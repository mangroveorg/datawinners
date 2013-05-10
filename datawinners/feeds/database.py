from django.conf import settings
from mangrove.datastore.database import get_db_manager
from datawinners.main.utils import get_database_name


def get_feed_database_name(user):
    return 'feed_' + get_database_name(user)


def get_feeds_database(user):
    if settings.FEEDS_ENABLED:
        return get_db_manager(server=settings.FEEDS_COUCH_SERVER, database=get_feed_database_name(user),credentials=settings.COUCHDBFEED_CREDENTIALS)
    return None




