from django.core.management.base import BaseCommand
from datawinners.main.datastore import document_stores, test_document_stores

from mangrove.bootstrap import initializer

from datawinners.main.utils import  sync_views
from mangrove.datastore.database import get_db_manager
from datawinners import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
            if "syncall" in args:
                db_names = document_stores()
            else:
                db_names = test_document_stores()

            for database_name in db_names:
                print ("Database %s") % (database_name,)
                print "Syncing Views....."
                manager = get_db_manager(server=settings.COUCH_DB_SERVER, database=database_name,
                    credentials=settings.COUCHDBMAIN_CREDENTIALS)
                initializer.sync_views(manager)
                sync_views(manager)
                print "Done."
