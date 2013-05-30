# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime
from django.conf import settings
from datawinners.accountmanagement.models import Organization, OrganizationSetting, DataSenderOnTrialAccount
from datawinners.feeds.database import feeds_db_for
from datawinners.main.utils import sync_feed_views
from mangrove.datastore.database import get_db_manager
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE
from mangrove.datastore.entity import create_entity
from mangrove.datastore.datadict import   get_or_create_data_dict
from mangrove.form_model.form_model import REPORTER, MOBILE_NUMBER_FIELD, NAME_FIELD
from mangrove.datastore.queries import get_entity_count_for_type

def create_feed_database(db_name):
    feed_manager = feeds_db_for('feed_'+db_name)
    assert feed_manager, "Could not create feed database manager for %s " % (db_name,)
    sync_feed_views(feed_manager)


def create_org_database(db_name):
    from datawinners.initializer import run

    manager = get_db_manager(server=settings.COUCH_DB_SERVER, database=db_name)
    assert manager, "Could not create database manager for %s " % (db_name,)
    run(manager)
    return manager


def create_org_and_feed_database(sender, user, request, **kwargs):
    profile = user.get_profile()
    org = Organization.objects.get(org_id=profile.org_id)
    active_organization(org)

    org_settings = OrganizationSetting.objects.get(organization=org)
    db_name = org_settings.document_store
    #    Explicitly create the new database. Should fail it db already exists.
    manager = create_org_database(db_name)
    if settings.FEEDS_ENABLED :
        create_feed_database(db_name)
    profile.reporter_id = make_user_as_a_datasender(manager, org, user.get_full_name(), profile.mobile_phone)
    profile.save()

    
def active_organization(org):
    if org is None:
        return None

    active_date = org.active_date

    if active_date is None:
        org.active_date = datetime.datetime.now().replace(microsecond=0)
        org.save()

def make_user_as_a_datasender(manager, organization, current_user_name, mobile_number):
    total_entity = get_entity_count_for_type(manager, [REPORTER])
    reporter_short_code = 'rep' + str(total_entity+1)
    entity = create_entity(dbm=manager, entity_type=REPORTER_ENTITY_TYPE, short_code=reporter_short_code,
        location=[organization.country_name()])
    mobile_number_type = get_or_create_data_dict(manager, name='Mobile Number Type', slug='mobile_number',
        primitive_type='string')
    name_type = get_or_create_data_dict(manager, name='Name', slug='name', primitive_type='string')
    data = [(MOBILE_NUMBER_FIELD, mobile_number, mobile_number_type), (NAME_FIELD, current_user_name, name_type)]
    entity.add_data(data=data)

    if organization.in_trial_mode:
        data_sender = DataSenderOnTrialAccount.objects.model(mobile_number=mobile_number,
            organization=organization)
        data_sender.save()
    return entity.short_code


