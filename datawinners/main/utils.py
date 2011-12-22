# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import os
from glob import iglob
import string

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from mangrove.datastore.database import get_db_manager
from mangrove.errors.MangroveException import UnknownOrganization, NumberNotRegisteredException

from datawinners.accountmanagement.models import Organization, OrganizationSetting, DataSenderOnTrialAccount, TEST_REPORTER_MOBILE_NUMBER
from datawinners.entity.helper import remove_hyphens

def get_database_manager(user):
    profile = user.get_profile()
    organization = Organization.objects.get(org_id=profile.org_id)
    organization_settings = OrganizationSetting.objects.get(organization=organization)
    db = organization_settings.document_store
    return get_db_manager(server=settings.COUCH_DB_SERVER, database=db)

def include_of_type(entity,type):
    return True if entity.type_path[0] == type else False

def exclude_of_type(entity,type):
    return False if entity.type_path[0] == type else True

def get_db_manager_for(data_sender_phone_no, org_tel_number):
    try:
        organization_settings = get_organization_settings_for(data_sender_phone_no, org_tel_number)
    except UnknownOrganization as ex:
        raise ex
    db = organization_settings.document_store
    return get_db_manager(server=settings.COUCH_DB_SERVER, database=db)

def get_organization_settings_for(data_sender_phone_no, org_tel_number, user=None):
    org_tel_number = remove_hyphens(org_tel_number)
    trial_account_phone_number = remove_hyphens(settings.TRIAL_ACCOUNT_PHONE_NUMBER)

    if org_tel_number == trial_account_phone_number:
        try:
            record = DataSenderOnTrialAccount.objects.get(mobile_number=data_sender_phone_no)
            organization_settings = OrganizationSetting.objects.get(organization=record.organization)
        except ObjectDoesNotExist:
            raise NumberNotRegisteredException(data_sender_phone_no)
    else:
        try:
            organization_settings = OrganizationSetting.objects.get(sms_tel_number=org_tel_number)
        except ObjectDoesNotExist:
            raise UnknownOrganization(org_tel_number)
    return organization_settings

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
    database_manager = dbm
    for v in view_js.keys():
        funcs = view_js[v]
        map = (funcs['map'] if 'map' in funcs else None)
        reduce = (funcs['reduce'] if 'reduce' in funcs else None)
        database_manager.create_view(v, map, reduce)


def exists_view(aggregation, database_manager):
    entity_type_views = database_manager._load_document('_design/datawinners_views')
    if entity_type_views is not None and entity_type_views['views'].get(aggregation):
        return True
    return False


def find_views():
    views = {}
    for fn in iglob(os.path.join(settings.PROJECT_DIR, 'main', 'couchview', '*.js')):
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
