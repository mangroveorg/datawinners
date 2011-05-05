# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.core.management.base import BaseCommand
from datawinners.main.initial_couch_fixtures import load_data
from mangrove.datastore.database import get_db_manager


class Command(BaseCommand):
    def handle(self, *args, **options):
        manager = get_db_manager()
        print ("Database %s") % (manager.database_name,)
        print "Loading....."
        load_data()
        print "Done."
