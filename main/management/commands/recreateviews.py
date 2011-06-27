from django.core.management.base import BaseCommand
from datawinners.main.initial_couch_fixtures import load_manager_for_default_test_account
from datawinners.main.utils import create_views
import mangrove


class Command(BaseCommand):

    def handle(self, *args, **options):
        manager = load_manager_for_default_test_account()
        print ("Database %s") % (manager.database_name,)
        print "Loading Views....."
        mangrove.datastore.views.create_views(manager)
        create_views(manager)
        print "Done."
