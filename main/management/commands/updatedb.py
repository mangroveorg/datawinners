from django.core.management.base import BaseCommand
from datawinners import settings, initializer
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.main.initial_couch_fixtures import load_manager_for_default_test_account, load_all_managers
from datawinners.main.utils import create_views, sync_views
import mangrove
from mangrove.datastore.database import get_db_manager


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
            print "Syncing....."
            initializer.run(manager)
            print "Done."
