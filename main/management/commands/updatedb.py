from django.core.management.base import BaseCommand
from datawinners import  initializer
from datawinners.main.initial_couch_fixtures import load_test_managers, load_all_managers


class Command(BaseCommand):
    def handle(self, *args, **options):
        if "syncall" in args:
            managers = load_all_managers()
        else:
            managers = load_test_managers()

        for manager in managers:
            print ("Database %s") % (manager.database_name,)
            print "Syncing....."
            initializer.run(manager)
            print "Done."
