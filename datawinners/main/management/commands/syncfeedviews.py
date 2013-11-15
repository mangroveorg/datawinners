import logging
from django.core.management.base import BaseCommand
from datawinners import settings
from datawinners.feeds.database import get_feed_db_from_main_db_name
from datawinners.main.management.commands.utils import document_stores_to_process
from datawinners.main.management.sync_changed_views import SyncOnlyChangedViews

logger = logging.getLogger(__name__)
class Command(BaseCommand):
    def handle(self, *args, **options):
        if settings.FEEDS_ENABLED:
            for database_name in document_stores_to_process(args):
                manager = get_feed_db_from_main_db_name(database_name)
                print ("Database %s") % (database_name,)
                logger.info("Database %s" %database_name)
                SyncOnlyChangedViews().sync_feed_views(manager)
                print "Done."
            return

        print "Feeds not enabled"
