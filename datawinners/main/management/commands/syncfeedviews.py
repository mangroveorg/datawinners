from django.conf import settings
from django.core.management.base import BaseCommand
from mangrove.datastore.database import get_db_manager
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.main.utils import  sync_feed_views

def load_all_managers():
    managers = []
    for org in OrganizationSetting.objects.all():
        db = 'feed_' + org.document_store
        manager = get_db_manager(server=settings.FEEDS_COUCH_SERVER, database=db,
            credentials=settings.COUCHDBFEED_CREDENTIALS)
        managers.append(manager)
    return managers


class Command(BaseCommand):
    def handle(self, *args, **options):
        managers = load_all_managers()

        for manager in managers:
            print ("Database %s") % (manager.database_name,)
            print "Syncing Feeds db....."
            sync_feed_views(manager)
            print "Done."
