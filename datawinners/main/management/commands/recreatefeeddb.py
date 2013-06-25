# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.core.management.base import BaseCommand
from datawinners.feeds.database import feeds_db_for, get_feed_db_from_main_db_name
from main.management.sync_changed_views import SyncOnlyChangedViews
from datawinners.main.management.commands.utils import document_stores_to_process
from mangrove.datastore.database import _delete_db_and_remove_db_manager
from datawinners import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        if settings.FEEDS_ENABLED:
            for database_name in document_stores_to_process(args):
                print ("Database %s") % (database_name,)
                print 'Deleting Feed DB...'
                manager = get_feed_db_from_main_db_name(database_name)
                _delete_db_and_remove_db_manager(manager)
                recreated_manager = feeds_db_for(database_name)
                print "Syncing Feed Views....."
                SyncOnlyChangedViews().sync_feed_views(recreated_manager)
            print "Feed database view sync done."
        else:
            print "Feeds not enabled"