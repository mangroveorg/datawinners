# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from datawinners.entity.import_data import load_subject_registration_data
from datawinners.location.LocationTree import get_location_tree
from mangrove import initializer
from mangrove.datastore.database import get_db_manager, _delete_db_and_remove_db_manager
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.entity import create_entity
from mangrove.datastore.entity_type import define_type
from mangrove.form_model.form_model import MOBILE_NUMBER_FIELD, NAME_FIELD
from mangrove.transport.player.player import SMSPlayer, TransportInfo, Request

class TestImportData(unittest.TestCase):
    def setUp(self):
        self.dbm = get_db_manager(database='mangrove-test')
        self._create_entities()
        self.player = SMSPlayer(self.dbm, get_location_tree())
        self.transport = TransportInfo(transport="sms", source="1234", destination="5678")
        initializer.run(self.dbm)

    def tearDown(self):
        _delete_db_and_remove_db_manager(self.dbm)


    def test_should_load_all_subjects(self):
        self._register_entities()

        subjects = load_subject_registration_data(self.dbm)

        self.assertEqual(4, len(subjects))

        self.assertEqual(subjects[0]['name'], 'clinic0')
        self.assertEqual(subjects[0]['geocode'], '1.0, 1.0')
        self.assertEqual(subjects[0]['mobile_number'], '--')

        self.assertEqual(subjects[1]['name'], 'clinic1')
        self.assertEqual(subjects[1]['mobile_number'], '--')

        self.assertEqual(subjects[2]['name'], 'clinic2')
        self.assertEqual(subjects[2]['mobile_number'], '12332114')

        self.assertEqual(subjects[3]['name'], 'clinic3')
        self.assertEqual(subjects[3]['geocode'], '--')
        self.assertEqual(subjects[3]['location'], 'pune')
        self.assertEqual(subjects[3]['description'], 'this is a clinic')


    def _create_entities(self):
        self.entity_type = ['clinic']
        define_type(self.dbm, self.entity_type)
        define_type(self.dbm, ['reporter'])
        self.name_type = DataDictType(self.dbm, name='Name', slug='name', primitive_type='string')
        self.telephone_number_type = DataDictType(self.dbm, name='telephone_number', slug='telephone_number',
                                                  primitive_type='string')
        rep1 = create_entity(self.dbm, ['reporter'], 'rep1')
        rep1.add_data(data=[(MOBILE_NUMBER_FIELD, '1234', self.telephone_number_type),
            (NAME_FIELD, "Test_reporter", self.name_type)], submission=dict(submission_id="2"))


    def _register_entity(self, text):
        self.player.accept(Request(transportInfo=self.transport, message=text))

    def _register_entities(self):
        self._register_entity('reg .t clinic .s 1 .g 1 1 .n clinic0')
        self._register_entity('reg .t clinic .s 2 .g 21 21 .n clinic1')
        self._register_entity('reg .t clinic .s 3 .g 11 11 .m 12332114 .n clinic2')
        self._register_entity('reg .t clinic .s 4 .d this is a clinic .l pune .n clinic3')
