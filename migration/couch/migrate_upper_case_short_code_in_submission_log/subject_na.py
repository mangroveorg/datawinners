# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from glob import iglob
import string
import os
from mangrove.datastore.database import get_db_manager, remove_db_manager

def all_dbs():
    import urllib2
    all_dbs = urllib2.urlopen("http://localhost:5984/_all_dbs").read()
    dbs = (eval(all_dbs))
    document_stores = filter(lambda x: x.startswith('hni_'), dbs)
    print "Document stores will be migrated:"
    print document_stores
    return document_stores


def find_subject():
        subjects = []
        for db in dbs:
            manager = get_db_manager(server="http://localhost:5984", database=db)
            database_query = manager.load_all_rows_in_view("subject_na")
            if database_query:
                print '%s (%d)' % (manager.database_name, len(database_query))
                subjects.extend(database_query)

            remove_db_manager(manager)

def sync_views(dbm):
    for fn in iglob(os.path.join(os.path.dirname(__file__), 'views', '*.coffee')):
        view_name = os.path.splitext(os.path.basename(fn))[0].split('_', 1)[1]
        with open(fn) as f:
            print 'Create view [%s] in database [%s]' % (view_name, dbm.database_name)
            dbm.create_view(view_name, f.read(), "", language="coffeescript")



def migrate():
    for db in dbs:
        dbm = get_db_manager(server="http://localhost:5984", database=db)
        sync_views(dbm)
        #///
#        find_subject()
#        find_formcode()

        remove_db_manager(dbm)


dbs = all_dbs()
migrate()
