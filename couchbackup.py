import urllib2, json

from couchdb import Server

COUCH_SERVER_URL = "http://178.79.185.35:5984/"

s = Server("http://localhost:5984")
url = urllib2.urlopen(COUCH_SERVER_URL + '_all_dbs')
data = url.read()
url.close()


dbs = json.loads(data)

dbs.remove('_users')

def delete_dbs():
    url = urllib2.urlopen('http://localhost:5984/_all_dbs')
    data = url.read()
    url.close()
    dbs = json.loads(data)
    dbs.remove('_users')
    dbs.remove('_replicator')
    for db in dbs:
        s.delete(db)
        
def replicate_dbs():
    for (index,db) in enumerate(dbs):
        print db
        print index
        s.create(db)
        print "Created DB %s" % db
        s.replicate(COUCH_SERVER_URL + db, 'http://localhost:5984/'+db)
        print "Started replication of %s" % db







