from django.conf import settings
from django.core.management.base import BaseCommand
from main.initial_couch_fixtures import load_all_feed_managers, load_test_feed_managers
from datawinners.main.utils import  sync_feed_views



class Command(BaseCommand):
    def handle(self, *args, **options):
        if settings.FEEDS_ENABLED:
            if "syncall" in args:
                managers = load_all_feed_managers()
            else:
                managers = load_test_feed_managers()

            for manager in managers:
                print ("Database %s") % (manager.database_name,)
                print "Syncing Feeds db....."
                sync_feed_views(manager)
                print "Done."
            return

        print "Feeds not enabled"
