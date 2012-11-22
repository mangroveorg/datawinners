import urllib2

def all_db_names(server):
    all_dbs = urllib2.urlopen(server + "/_all_dbs").read()
    dbs = eval(all_dbs)
    return filter(lambda x: x.startswith('hni_'), dbs)
