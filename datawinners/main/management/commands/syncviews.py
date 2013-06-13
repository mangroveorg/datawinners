from django.core.management.base import BaseCommand
from datawinners.main.database import  get_db_manager
from main.management.sync_changed_views import SyncOnlyChangedViews
from main.management.commands.utils import document_stores_to_process


class Command(BaseCommand):
    def handle(self, *args, **options):
        for database_name in document_stores_to_process(args):
            print ("Database %s") % (database_name)
            manager = get_db_manager(database_name)
            SyncOnlyChangedViews().sync_view(manager)
            print "Done."


