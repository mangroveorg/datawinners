from django.core.management.base import BaseCommand
from datawinners import  initializer
from datawinners.main.database import get_db_manager
from main.management.commands.utils import document_stores_to_process


class Command(BaseCommand):
    def handle(self, *args, **options):
        for database_name in document_stores_to_process(args):
            manager = get_db_manager(database_name)
            print ("Database %s") % (database_name)
            print "Syncing....."
            initializer.run(manager)
            print "Done."
