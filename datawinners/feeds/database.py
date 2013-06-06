from django.conf import settings
from mangrove.datastore.database import get_db_manager

def feeds_db_name(database_name):
    return 'feed_' + database_name

def get_feed_database_name(user):
    from datawinners.main.utils import get_database_name
    database_name = get_database_name(user)
    return feeds_db_name(database_name)

def get_feed_db_from_main_db_name(db_name):
    return feeds_db_for(feeds_db_name(db_name))

def feeds_db_for(db_name):
    return get_db_manager(server=settings.FEEDS_COUCH_SERVER, database=db_name,
        credentials=settings.COUCHDBFEED_CREDENTIALS)


def get_feeds_database(user):
    if settings.FEEDS_ENABLED:
        db_name = get_feed_database_name(user)
        return feeds_db_for(db_name)
    return None


def get_feeds_db_for_org(organization):
    from datawinners.accountmanagement.models import OrganizationSetting
    if settings.FEEDS_ENABLED:
        organization_settings = OrganizationSetting.objects.get(organization=organization)
        return feeds_db_for(feeds_db_name(organization_settings.document_store))
    return None

