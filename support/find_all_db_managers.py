from mangrove.datastore.database import get_db_manager

def all_dbs():
    import urllib2
    all_dbs = urllib2.urlopen("http://localhost:5984/_all_dbs").read()
    dbs_ = (eval(all_dbs))
    result = []

    for db in dbs_:
        if db[0] != '_':
            result.append(db)

    return result