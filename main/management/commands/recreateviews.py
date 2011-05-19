from django.core.management.base import BaseCommand
import datawinners
from datawinners.main.initial_couch_fixtures import load_manager_for_default_test_account
from datawinners.main.utils import create_all_views
import mangrove


class Command(BaseCommand):

    def handle(self, *args, **options):
        manager = load_manager_for_default_test_account()
        print ("Database %s") % (manager.database_name,)
        print "Loading Views....."
        create_all_views(manager)
        print "Done."


