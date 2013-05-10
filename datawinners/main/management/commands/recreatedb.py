# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf import settings
from django.core.management.base import BaseCommand
from datawinners.main.initial_couch_fixtures import load_data, load_test_managers, load_all_managers
from mangrove.datastore.database import _delete_db_and_remove_db_manager, get_db_manager
from mangrove.bootstrap import initializer


class Command(BaseCommand):
    def handle(self, *args, **options):
        if "syncall" in args:
            managers = load_all_managers()
        else:
            managers = load_test_managers()

        for manager in managers:
            print ("Database %s") % (manager.database_name,)
            print 'Deleting...'
            _delete_db_and_remove_db_manager(manager)
            recreated_manager = get_db_manager(server=settings.COUCH_DB_SERVER, database=manager.database_name,
                credentials=settings.COUCHDBMAIN_CREDENTIALS)
            print "Syncing Views....."
            initializer.sync_views(recreated_manager)

        print "Loading data....."
        load_data()

        print "Done."

