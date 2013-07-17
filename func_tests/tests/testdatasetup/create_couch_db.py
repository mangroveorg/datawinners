# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest

import os
from couchdb.client import Server
from framework.utils.couch_http_wrapper import CouchHttpWrapper


class TestCouchHTTPWrapper(unittest.TestCase):
    DATA_STORE = 'mangrove_web'

    def test_exported_data_to_couch(self):
        self.export_test_data_to_couch()
        server = Server()
        db = server[self.DATA_STORE]
        assert db['nogo@mail.com']

    def export_test_data_to_couch(self):
        http_wrapper = CouchHttpWrapper()
        http_wrapper.deleteDb(self.DATA_STORE)
        http_wrapper.createDb(self.DATA_STORE)
        test_data_dir = os.path.join(os.path.dirname(__file__), '../../testdata/')
        fp = open(test_data_dir + 'functional_test_data.json')
        http_wrapper.saveBulkDoc(self.DATA_STORE, fp.read())
        fp.close()


if __name__ == "__main__":
    unittest.main()
