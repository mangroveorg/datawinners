# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import os

os.environ['DJANGO_SETTINGS_MODULE'] = "datawinners.settings"

import settings
from datawinners.accountmanagement.models import OrganizationSetting
from find_all_db_managers import all_db_names
from mangrove.datastore.database import get_db_manager, remove_db_manager

db_server = "http://localhost:5984"

map_project_id_to_organization = """
function(doc) {
    if (doc.document_type == 'Project') {
        if(!doc.void && doc._id =='49bd74ec28e011e297bcfefdb24fb922' ){
            emit([doc.created,doc.name], doc);
        }
    }
}
"""


def find_organization():

    dbs = all_db_names(db_server)
    for db in dbs:
        print db
        manager = get_db_manager(server=db_server, database=db,credentials=settings.COUCHDBMAIN_CREDENTIALS)
        database_query = manager.database.query(map_project_id_to_organization)
        if database_query:
            organization_setting = OrganizationSetting.objects.filter(document_store=db)[0]
            organization_name = organization_setting.organization.name
            print ("********************************************")
            print "Document store: %s" % db
            print "Organization name: %s" % organization_name

            break
        remove_db_manager(manager)
find_organization()
