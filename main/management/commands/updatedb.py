from django.core.management.base import BaseCommand
from datawinners import  initializer
from datawinners.main.initial_couch_fixtures import load_manager_for_default_test_account, load_all_managers


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
