# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datawinners

from datawinners.accountmanagement.models import NGOUserProfile, OrganizationSettings
from mangrove.datastore.database import get_db_manager


def ngo_user_created(sender, user, request, **kwargs):
    data = NGOUserProfile()
    data.org_id = kwargs['organization_id']
    data.title = kwargs['title']
    data.user = user
    print 'saving the user'
    data.save()

def create_org_database(sender, user, request, **kwargs):
    org = kwargs.get('organization')
    if org is None:
        return None
    org_settings = OrganizationSettings.objects.get(organization=org)
    db = org_settings.document_store
    manager = get_db_manager(server=datawinners.settings.COUCH_DB_SERVER, database=db)
    assert manager,"Could not create database manager for %s " % (db,)


from registration.signals import user_registered
user_registered.connect(ngo_user_created)
user_registered.connect(create_org_database)



