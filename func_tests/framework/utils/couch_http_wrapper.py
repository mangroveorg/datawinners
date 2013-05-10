# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import base64

import httplib
import json
import simplejson
import settings


def prettyPrint(s):
    """Prettyprints the json response of an HTTPResponse object"""

    # HTTPResponse instance -> Python object -> str
    print simplejson.dumps(json.loads(s.read()), sort_keys=True, indent=4)


class CouchHttpWrapper(object):
    """Basic wrapper class for operations on a couchDB"""

    def __init__(self, host, port=5984, options=None):
        self.host = host
        self.port = port

    def connect(self):
        return httplib.HTTPConnection(self.host, self.port)  # No close()

    # Database operations

    def createDb(self, dbName):
        """Creates a new database on the server"""

        r = self.put(''.join(['/', dbName, '/']), "")
        prettyPrint(r)

    def deleteDb(self, dbName):
        """Deletes the database on the server"""

        r = self.delete(''.join(['/', dbName, '/']))
        prettyPrint(r)

    def listDb(self):
        """List the databases on the server"""

        prettyPrint(self.get('/_all_dbs'))

    def infoDb(self, dbName):
        """Returns info about the couchDB"""
        r = self.get(''.join(['/', dbName, '/']))
        prettyPrint(r)

    # Document operations

    def listDoc(self, dbName):
        """List all documents in a given database"""

        r = self.get(''.join(['/', dbName, '/', '_all_docs']))
        prettyPrint(r)

    def openDoc(self, dbName, docId):
        """Open a document in a given database"""
        r = self.get(''.join(['/', dbName, '/', docId, ]))
        prettyPrint(r)
        return r

    def saveDoc(self, dbName, body, docId=None):
        """Save/create a document to/in a given database"""
        if docId:
            r = self.put(''.join(['/', dbName, '/', docId]), body)
        else:
            r = self.post(''.join(['/', dbName, '/']), body)
        prettyPrint(r)

    def saveBulkDoc(self, dbName, body):
        """Save/create multiple documents to/in a given database using HttpBulkAPI"""
        r = self.post(''.join(['/', dbName, '/_bulk_docs']), body)
        prettyPrint(r)

    def deleteDoc(self, dbName, docId, rev_id):
        # XXX Crashed if resource is non-existent; not so for DELETE on db. Bug?
        # XXX Does not work any more, on has to specify an revid
        #     Either do html head to get the recten revid or provide it as parameter
        r = self.delete(''.join(['/', dbName, '/', docId, '?revid=', rev_id]))
        prettyPrint(r)

    # Basic http methods

    def get(self, uri):
        c = self.connect()
        base64_couchdbmain_credentials = base64.encodestring('%s:%s' %settings.COUCHDBMAIN_CREDENTIALS)[:-1]
        headers = {
            "Accept": "application/json",
            "Authorization": "Basic %s" % base64_couchdbmain_credentials}
        c.request("GET", uri, None, headers)
        return c.getresponse()

    def post(self, uri, body):
        c = self.connect()
        headers = {"Content-type": "application/json"}
        c.request('POST', uri, body, headers)
        return c.getresponse()

    def put(self, uri, body):
        c = self.connect()
        if len(body) > 0:
            headers = {"Content-type": "application/json"}
            c.request("PUT", uri, body, headers)
        else:
            c.request("PUT", uri, body)
        return c.getresponse()

    def delete(self, uri):
        c = self.connect()
        c.request("DELETE", uri)
        return c.getresponse()
