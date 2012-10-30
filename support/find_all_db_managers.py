def all_db_names(server):
    import urllib2

    all_dbs = urllib2.urlopen(server + "/_all_dbs").read()
    dbs = (eval(all_dbs))
    document_stores = filter(lambda x: x.startswith('hni_'), dbs)
    return document_stores