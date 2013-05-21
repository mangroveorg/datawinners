import couchdb

SERVER = 'http://localhost:5984/'
COUCHDB_USERNAME = 'admin'
COUCHDB_PASSWORD = 'admin'
COUCHDB_CREDENTIALS = (COUCHDB_USERNAME, COUCHDB_PASSWORD)
log_file = open('/var/log/datawinners/couchdb_document_stats.log', 'a')

def print_stats(server, db):
    document_count = server[db].info()['doc_count']
    print "%s : %s" % (db, document_count)
    log_file.writelines("%s : %s \n" % (db, document_count))

def get_couchdb_stats():
    server = couchdb.Server(SERVER)
    server.resource.credentials = COUCHDB_CREDENTIALS
    for db in server:
        if not db.startswith("_") :
            print_stats(server, db)

get_couchdb_stats()