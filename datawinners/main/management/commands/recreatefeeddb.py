# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf import settings
from django.core.management.base import BaseCommand
from datawinners.main.initial_couch_fixtures import  load_all_feed_managers, load_test_feed_managers
from datawinners.feeds.database import feeds_db_for
from datawinners.initializer import sync_feed
from mangrove.datastore.database import _delete_db_and_remove_db_manager


class Command(BaseCommand):
    def handle(self, *args, **options):
        if settings.FEEDS_ENABLED:
            if "syncall" in args:
                managers = load_all_feed_managers()
            else:
                managers = load_test_feed_managers()

            for manager in managers:
                print ("Database %s") % (manager.database_name,)
                print 'Deleting Feed DB...'
                _delete_db_and_remove_db_manager(manager)
                recreated_manager = feeds_db_for(manager.database_name)
                print "Syncing Feed Views....."
                sync_feed(recreated_manager)

            print "Feed databases done."
            return
        print "Feeds not enabled"