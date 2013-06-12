# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.core.management.base import BaseCommand
from datawinners.main.initial_couch_fixtures import load_data
from datawinners.main.datastore import document_stores, test_document_stores
from mangrove.datastore.database import _delete_db_and_remove_db_manager, get_db_manager
from mangrove.bootstrap import initializer
from datawinners import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        if "syncall" in args:
            db_names = document_stores()
        else:
            db_names = test_document_stores()

        for database_name in db_names:
            print ("Database %s") % (database_name,)
            print 'Deleting...'
            manager = get_db_manager(server=settings.COUCH_DB_SERVER, database=database_name,
                credentials=settings.COUCHDBMAIN_CREDENTIALS)
            _delete_db_and_remove_db_manager(manager)
            recreated_manager = get_db_manager(server=settings.COUCH_DB_SERVER, database=database_name,
                credentials=settings.COUCHDBMAIN_CREDENTIALS)
            print "Syncing Views....."
            initializer.sync_views(recreated_manager)

        print "Loading data....."
        load_data()

        print "Done."

