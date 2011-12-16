from django.core.management.base import BaseCommand
from datawinners.main.initial_couch_fixtures import load_test_managers, load_all_managers
from datawinners.main.utils import  sync_views
import mangrove


class Command(BaseCommand):
    def handle(self, *args, **options):
        if "syncall" in args:
            managers = load_all_managers()
        else:
            managers = load_test_managers()

        for manager in managers:
            print ("Database %s") % (manager.database_name,)
            print "Syncing Views....."
            mangrove.datastore.views.sync_views(manager)
            sync_views(manager)
            print "Done."
