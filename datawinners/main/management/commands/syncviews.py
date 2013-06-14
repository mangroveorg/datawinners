from django.core.management.base import BaseCommand
import sys
from datawinners.main.database import  get_db_manager
from main.management.sync_changed_views import SyncOnlyChangedViews
from main.management.commands.utils import document_stores_to_process
import traceback

class Command(BaseCommand):
    def handle(self, *args, **options):
        for database_name in document_stores_to_process(args):
            print "Database %s" % database_name
            manager = get_db_manager(database_name)
            try:
                SyncOnlyChangedViews().sync_view(manager)
            except Exception as e:
                print "ERROR " + e.message
                traceback.print_exc(file=sys.stdout)
            print "Done."


