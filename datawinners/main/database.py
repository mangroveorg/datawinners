from datawinners.main.utils import get_database_name
from mangrove.datastore.database import get_db_manager as mangrove_db_manager
from datawinners import settings


def get_db_manager(database_name):
    return mangrove_db_manager(server=settings.COUCH_DB_SERVER, database=database_name,
        credentials=settings.COUCHDBMAIN_CREDENTIALS)


def get_database_manager(user):
    return get_db_manager(get_database_name(user))