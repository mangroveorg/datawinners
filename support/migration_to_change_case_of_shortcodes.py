import re
import sys
from mangrove.datastore.database import get_db_manager

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")
from datawinners.main.couchdb.utils import all_db_names
from mangrove.datastore.entity import get_all_entities


def get_DS_with_ca(dbname):
    dbm = get_db_manager(server="http://admin:admin@172.18.9.6:5984", database=dbname,credentials = ('admin','admin'))
    all_ds = get_all_entities(dbm, ['reporter'])
    for ds in all_ds:
        if 'short_code' in ds.data.keys():
            short_code = ds.data['short_code']['value']
            if re.search('[A-Z]', short_code):
                print 'short_code is :'+short_code
                print 'database is :'+dbname

for db in all_db_names(server="http://admin:admin@172.18.9.6:5984"):
    get_DS_with_ca(db)