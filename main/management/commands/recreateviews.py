from django.core.management.base import BaseCommand
from datawinners.main.initial_couch_fixtures import load_manager_for_default_test_account
from datawinners.settings import PROJECT_DIR

import os
from glob import iglob
import string


class Command(BaseCommand):
    def handle(self, *args, **options):
        manager = load_manager_for_default_test_account()
        print ("Database %s") % (manager.database_name,)
        print "Loading Views....."
        create_views(manager)
        print "Done."


def create_views(dbm):
    '''Creates a standard set of views in the database'''
    global view_js
    database_manager = dbm
    for v in view_js.keys():
        if not exists_view(v, database_manager):
            funcs = view_js[v]
            map = (funcs['map'] if 'map' in funcs else None)
            reduce = (funcs['reduce'] if 'reduce' in funcs else None)
            database_manager.create_view(view_name=v, map=map, reduce=reduce, view_document='datawinners_views')


def exists_view(aggregation, database_manager):
    entity_type_views = database_manager._load_document('_design/datawinners_views')
    if entity_type_views is not None and entity_type_views['views'].get(aggregation):
        return True
    return False


def find_views():
    views = {}
    for fn in iglob(os.path.join(PROJECT_DIR, 'main', 'couchview', '*.js')):
        try:
            func, name = string.split(os.path.splitext(os.path.basename(fn))[0], '_', 1)
            with open(fn) as f:
                if name not in views:
                    views[name] = {}
                views[name][func] = f.read()
        except Exception:
            # doesn't match pattern, or file could be read, just skip
            pass
    return views

view_js = find_views()
