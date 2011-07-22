# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from mock import Mock
from datawinners.entity.import_data import import_data
from mangrove import initializer
from mangrove.datastore.database import get_db_manager, _delete_db_and_remove_db_manager
from mangrove.datastore.entity import get_entity_count_for_type

class TestImport(unittest.TestCase):
    def setUp(self):
        self.dbm = get_db_manager(database='mangrove-test')
        self.csv_data = """
"form_code","t","n","l","g","d","s","m"
"REG","reporter","Aàman Farafangana ","Farafangana ","-21.8  46.8333","This is a Clinic in near to Farafangana ",,987654328
"REG","reporter","Reporter1 Fianarantsoa ","mahajanga ","-20.45  45.1","C'est une clinique à Fianarantsoa",,987654329
"REG","reporter","Reporter2 Maintirano ","Maintirano ","-18.05  44.0333","This is a reporter in Maintirano ",,987654333
"REG","reporter","Reporter3 Mananjary ","Mananjary ","-21.2  48.3667","This is a reporter in Mananjary ",,987654334
"""
        initializer.run(self.dbm)

    def tearDown(self):
        _delete_db_and_remove_db_manager(self.dbm)

    def test_should_import_data_senders(self):
        file_name = "reporters.csv"
        request = Mock()
        request.GET = {'qqfile' : file_name}
        request.raw_post_data = self.csv_data
        error_message, failure_imports, success, success_message = import_data(request=request,manager = self.dbm)
        self.assertTrue(success)
        self.assertEqual(4,get_entity_count_for_type(self.dbm,entity_type="reporter"))
