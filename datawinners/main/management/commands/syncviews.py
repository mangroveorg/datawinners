from django.core.management.base import BaseCommand
from datawinners.main.datastore import test_document_stores, document_stores

from mangrove.bootstrap.initializer import sync_views as mangrove_sync_views

from datawinners.main.utils import sync_views as datawinners_sync_views
from mangrove.datastore.database import get_db_manager
from datawinners import settings



class Command(BaseCommand):
    def handle(self, *args, **options):
        if "syncall" in args:
            db_names = document_stores()
        else:
            db_names = test_document_stores()

        for database_name in db_names:
            print ("Database %s") % (database_name)
            print "Syncing....."
            manager = get_db_manager(server=settings.COUCH_DB_SERVER, database=database_name,
                credentials=settings.COUCHDBMAIN_CREDENTIALS)
            datawinners_sync_views(manager)
            mangrove_sync_views(manager)
            print "Done."
