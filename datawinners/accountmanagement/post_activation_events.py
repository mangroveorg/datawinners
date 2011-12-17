# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime
from django.conf import settings
from datawinners.accountmanagement.models import Organization, OrganizationSetting,NGOUserProfile
from mangrove.datastore.database import get_db_manager


def create_org_database(sender, user, request, **kwargs):
    from datawinners.initializer import run

    profile = user.get_profile()
    org = Organization.objects.get(org_id=profile.org_id)
    active_organization(org)

    org_settings = OrganizationSetting.objects.get(organization=org)
    db_name = org_settings.document_store
    #    Explicitly create the new database. Should fail it db already exists.
    manager = get_db_manager(server=settings.COUCH_DB_SERVER, database=db_name)
    assert manager, "Could not create database manager for %s " % (db_name,)
    run(manager)
    
def active_organization(org):
    if org is None:
        return None

    active_date = org.active_date

    if active_date is None:
        org.active_date = datetime.datetime.now().replace(microsecond=0)
        org.save()
