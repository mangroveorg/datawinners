from django.conf import settings
from mangrove.datastore.database import get_db_manager
from datawinners.main.utils import get_database_name
from datawinners.accountmanagement.models import OrganizationSetting

def get_feed_database_name(user):
    return 'feed_' + get_database_name(user)


def feeds_db_for(db_name):
    return get_db_manager(server=settings.FEEDS_COUCH_SERVER, database=db_name,
        credentials=settings.COUCHDBFEED_CREDENTIALS)


def get_feeds_database(user):
    if settings.FEEDS_ENABLED:
        db_name = get_feed_database_name(user)
        return feeds_db_for(db_name)
    return None


def get_feeds_db_for_org(organization):
    if settings.FEEDS_ENABLED:
        organization_settings = OrganizationSetting.objects.get(organization=organization)
        db = 'feed_' + organization_settings.document_store
        return feeds_db_for(db)
    return None

