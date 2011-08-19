from django.core.management.base import BaseCommand
from datawinners.main.initial_couch_fixtures import load_manager_for_default_test_account, load_all_managers
from datawinners.main.utils import  sync_views
import mangrove


class Command(BaseCommand):

    def handle(self, *args, **options):
        managers = []
        if "syncall" in args:
            managers = load_all_managers()
        else:
            manager = load_manager_for_default_test_account()
            managers.append(manager)

        for manager in managers:
            print ("Database %s") % (manager.database_name,)
            print "Syncing Views....."
            mangrove.datastore.views.sync_views(manager)
            sync_views(manager)
            print "Done."
