from django.core.management.base import BaseCommand
from datawinners.initializer import sync_feed
from feeds.database import get_feed_db_from_main_db_name
from main.database import document_stores, test_document_stores
from datawinners import settings
from main.management.commands.utils import document_stores_to_process


class Command(BaseCommand):
    def handle(self, *args, **options):
        if settings.FEEDS_ENABLED:
            for database_name in document_stores_to_process(args):
                manager = get_feed_db_from_main_db_name(database_name)
                print ("Database %s") % (database_name,)
                print "Syncing Feeds db....."
                sync_feed(manager)
                print "Done."
            return

        print "Feeds not enabled"
