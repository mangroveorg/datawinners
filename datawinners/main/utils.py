# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime
import logging
from django.http import HttpRequest
import os
from glob import iglob
import string

from django.conf import settings

from mangrove.datastore.database import get_db_manager

from datawinners.accountmanagement.models import Organization, OrganizationSetting


performance_logger = logging.getLogger("performance")

def get_database_manager(user):
    db = get_database_name(user)
    return get_db_manager(server=settings.COUCH_DB_SERVER, database=db , credentials = settings.COUCHDBMAIN_CREDENTIALS)

def get_database_name(user):
    profile = user.get_profile()
    organization = Organization.objects.get(org_id=profile.org_id)
    organization_settings = OrganizationSetting.objects.get(organization=organization)
    return organization_settings.document_store

def include_of_type(entity, type):
    return entity.type_path[0] == type

def exclude_of_type(entity, type):
    return not include_of_type(entity, type)

def create_views(dbm):
    """Creates a standard set of views in the database"""
    global view_js
    database_manager = dbm
    for v in view_js.keys():
        if not exists_view(v, database_manager):
            funcs = view_js[v]
            map = (funcs['map'] if 'map' in funcs else None)
            reduce = (funcs['reduce'] if 'reduce' in funcs else None)
            database_manager.create_view(view_name=v, map=map, reduce=reduce)


def sync_views(dbm):
    """Updates or Creates a standard set of views in the database"""
    global view_js
    sync_views_functions(dbm, view_js)


def sync_feed_views(dbm):
    """Updates or Creates a standard set of views in the feeds database"""
    view_js = find_views('feedview')
    sync_views_functions(dbm, view_js)

def sync_views_functions(dbm, view_js):
    for v in view_js.keys():
        funcs = view_js[v]
        map = (funcs['map'] if 'map' in funcs else None)
        reduce = (funcs['reduce'] if 'reduce' in funcs else None)
        dbm.create_view(v, map, reduce)


def exists_view(aggregation, database_manager):
    entity_type_views = database_manager._load_document('_design/datawinners_views')
    if entity_type_views is not None and entity_type_views['views'].get(aggregation):
        return True
    return False


def find_views(db_view_dir):
    views = {}
    for fn in iglob(os.path.join(settings.PROJECT_DIR, 'main', db_view_dir, '*.js')):
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

def timebox(view_func):
    def _wrapped_view(*args, **kwargs):
        start_time = datetime.datetime.now()

        result = view_func(*args, **kwargs)

        end_time = datetime.datetime.now()
        time_elapsed = (end_time - start_time).total_seconds()
        request = args[0]

        if isinstance(request, HttpRequest):
            performance_logger.info("[%s] method: %s, user: %s, time used %f seconds." % (request.method, view_func.func_name, request.user, time_elapsed))
        else:
            performance_logger.info("method: %s, time used %f seconds." % (view_func.func_name, time_elapsed))

        return result
    return _wrapped_view


view_js = find_views('couchview')
