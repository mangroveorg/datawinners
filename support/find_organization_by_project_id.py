# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import logging
from find_all_db_managers import all_dbs
from mangrove.datastore.database import get_db_manager, remove_db_manager

managers = all_dbs()

map_project_id_to_organization = """
function(doc) {
    if (doc.document_type == 'Project') {
        if(!doc.void && doc._id =='ad8f4ce2175711e2a608fefdb24fb922' ){
            emit([doc.created,doc.name], doc);
        }
    }
}
"""

logger = logging.getLogger("django")

def find_organization():
    result = {}

    managers = all_dbs()
    for manager_name in managers:
        logger.info(manager_name)
        manager = get_db_manager(server="http://localhost:5984", database=manager_name)
        database_query = manager.database.query(map_project_id_to_organization)
        if database_query:
            logger.info("**********************pro found**********************" + manager_name)
        remove_db_manager(manager)
find_organization()
