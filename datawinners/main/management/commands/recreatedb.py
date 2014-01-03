# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.core.management.base import BaseCommand
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.initial_couch_fixtures import load_data
from datawinners.main.database import get_db_manager
from datawinners.main.management.sync_changed_views import SyncOnlyChangedViews
from datawinners.main.management.commands.utils import document_stores_to_process
from mangrove.datastore.cache_manager import get_cache_manager
from mangrove.datastore.database import _delete_db_and_remove_db_manager


class Command(BaseCommand):
    def handle(self, *args, **options):
        get_cache_manager().flush_all()
        for database_name in all_db_names():
            print ("Database %s") % (database_name,)
            print 'Deleting...'
            manager = get_db_manager(database_name)
            _delete_db_and_remove_db_manager(manager)

        for database_name in document_stores_to_process(args):
            recreated_manager = get_db_manager(database_name)
            print "Syncing Views....."
            SyncOnlyChangedViews().sync_view(recreated_manager)
        print "Loading data....."
        load_data()
        print "Done."
