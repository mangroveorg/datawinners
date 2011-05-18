# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.base import Model
from datawinners.accountmanagement.models import Organization, OrganizationSettings
from mangrove.datastore.database import get_db_manager
from  datawinners import settings
from mangrove.errors.MangroveException import UnknownOrganization

def get_database_manager_for_user(user):
    profile = user.get_profile()
    organization = Organization.objects.get(org_id=profile.org_id)
    organization_settings = OrganizationSettings.objects.get(organization=organization)
    db = organization_settings.document_store
    return get_db_manager(server=settings.COUCH_DB_SERVER, database=db)


def get_database_manager(request):
    user = request.user
    return get_database_manager_for_user(user)


def get_db_manager_for(org_tel_number):
    try:
        organization_settings = OrganizationSettings.objects.get(sms_tel_number=org_tel_number)
    except ObjectDoesNotExist:
        raise UnknownOrganization(org_tel_number)
    db = organization_settings.document_store
    return get_db_manager(server=settings.COUCH_DB_SERVER, database=db)