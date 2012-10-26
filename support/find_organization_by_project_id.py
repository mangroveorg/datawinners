# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import logging
from find_all_db_managers import all_db_names
from mangrove.datastore.database import get_db_manager, remove_db_manager

db_server = "http://10.18.2.237:5984"

map_project_id_to_organization = """
function(doc) {
    if (doc.document_type == 'Project') {
        if(!doc.void && doc._id =='015caee0ffb311e0bc9afefdb24fb922' ){
            emit([doc.created,doc.name], doc);
        }
    }
}
"""

logger = logging.getLogger("django")

def find_organization():

    managers = all_db_names(db_server)
    for manager_name in managers:
        logger.info(manager_name)
        print manager_name
        manager = get_db_manager(server=db_server, database=manager_name)
        database_query = manager.database.query(map_project_id_to_organization)
        if database_query:
            logger.info("**********************pro found**********************" + manager_name)
            print ("**********************pro found**********************" + manager_name)
        remove_db_manager(manager)
find_organization()
