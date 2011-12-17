# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from mock import Mock
from django.test import TestCase
from datawinners.entity.import_data import import_data
from mangrove.bootstrap import initializer
from mangrove.datastore.database import get_db_manager, _delete_db_and_remove_db_manager
from mangrove.datastore.queries import get_entity_count_for_type

class TestImport(TestCase):
    def setUp(self):
        self.dbm = get_db_manager(database='mangrove-test')
        self.csv_data = """
"form_code","t","n","l","g","d","s","m"
"REG","reporter","Aàman Farafangana ","Farafangana ","-21.8  46.8333","This is a Clinic in near to Farafangana ","r1",987654328
"REG","reporter","Reporter1 Fianarantsoa ","mahajanga ","-20.45  45.1","C'est une clinique à Fianarantsoa","r2",987654329
"REG","reporter","Reporter2 Maintirano ","Maintirano ","-18.05  44.0333","This is a reporter in Maintirano ","r3",987654333
"REG","reporter","Reporter3 Mananjary ","Mananjary ","-21.2  48.3667","This is a reporter in Mananjary ","r4",987654334
"""
        initializer.run(self.dbm)

    def tearDown(self):
        _delete_db_and_remove_db_manager(self.dbm)

    def test_should_import_data_senders(self):
        file_name = "reporters.csv"
        request = Mock()
        request.GET = {'qqfile': file_name}
        request.raw_post_data = self.csv_data
        error_message, failure_imports, success_message, imported_entities = import_data(request=request,
                                                                                         manager=self.dbm)
        self.assertEqual(4, get_entity_count_for_type(self.dbm, entity_type="reporter"))
        self.assertEqual(4, len(imported_entities))
        self.assertEqual('reporter', imported_entities["r1"])
        self.assertEqual('reporter', imported_entities["r2"])
        self.assertEqual('reporter', imported_entities["r3"])
        self.assertEqual('reporter', imported_entities["r4"])
