def all_db_names(server):
    import urllib2
    all_dbs = urllib2.urlopen(server + "/_all_dbs").read()
    dbs_ = (eval(all_dbs))
    result = []

    for db in dbs_:
        if db[0] != '_':
            result.append(db)

    return result