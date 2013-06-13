from django.core.management.base import BaseCommand
from datawinners.main.database import  get_db_manager
from main.management.commands.utils import document_stores_to_process
from mangrove.bootstrap import initializer
from datawinners.main.utils import  sync_views


class Command(BaseCommand):
    def handle(self, *args, **options):
        for database_name in document_stores_to_process(args):
            print ("Database %s") % (database_name,)
            print "Syncing Views....."
            manager = get_db_manager(database_name)
            #force sync all views
            initializer.sync_views(manager)
            sync_views(manager)
            print "Done."
