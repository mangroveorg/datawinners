# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import couchdb
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
    from datawinners.initializer import run
    org = kwargs.get('organization')
    if org is None:
        return None
    org_settings = OrganizationSettings.objects.get(organization=org)
    db_name = org_settings.document_store
    #    Explicitly create the new database. Should fail it db already exists.
    server = couchdb.client.Server(datawinners.settings.COUCH_DB_SERVER)
    server.create(db_name)
    manager = get_db_manager(server=datawinners.settings.COUCH_DB_SERVER, database=db_name)
    assert manager,"Could not create database manager for %s " % (db_name,)
    run(manager)
