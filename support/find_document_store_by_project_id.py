# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import logging
from find_all_db_managers import all_db_names
from mangrove.datastore.database import get_db_manager, remove_db_manager

db_server = "http://10.18.2.237:5984"

map_project_id_to_organization = """
function(doc) {
    if (doc.document_type == 'Project') {
        if(!doc.void && doc._id =='25f80836ece711e18d91fefdb24fb922' ){
            emit([doc.created,doc.name], doc);
        }
    }
}
"""

logger = logging.getLogger("django")

def find_organization():

    dbs = all_db_names(db_server)
    for db in dbs:
        logger.info(db)
        print db
        manager = get_db_manager(server=db_server, database=db)
        database_query = manager.database.query(map_project_id_to_organization)
        if database_query:
            logger.info("********************** document store found **********************\n" + db)
            print ("********************** document store found **********************\n" + db)

            break
        remove_db_manager(manager)
find_organization()
