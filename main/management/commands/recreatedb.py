# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.core.management.base import BaseCommand
from datawinners.main.initial_couch_fixtures import load_data, load_manager_for_default_test_account
from datawinners.main.utils import create_views
import mangrove
from mangrove.datastore.database import _delete_db_and_remove_db_manager


class Command(BaseCommand):
    def handle(self, *args, **options):
        manager = load_manager_for_default_test_account()
        print ("Deleting %s.....") % (manager.database_name,)
        _delete_db_and_remove_db_manager(manager)
        manager = load_manager_for_default_test_account()
        print "Loading All View"
        mangrove.datastore.views.create_views(manager)
        create_views(manager)
        print "Loading data....."
        load_data()
        print "Done."
