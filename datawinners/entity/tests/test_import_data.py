# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase
from datawinners.entity.import_data import load_subject_registration_data
from datawinners.location.LocationTree import get_location_tree
from mangrove.bootstrap import initializer
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.entity import create_entity
from mangrove.datastore.entity_type import define_type
from mangrove.form_model.form_model import MOBILE_NUMBER_FIELD, NAME_FIELD, get_form_model_by_code
from mangrove.transport.player.parser import KeyBasedSMSParser
from mangrove.transport.player.player import SMSPlayer
from mangrove.transport import TransportInfo
from datawinners.location.LocationTree import get_location_hierarchy

class TestImportData(MangroveTestCase):
    def setUp(self):
        MangroveTestCase.setUp(self)
        self._create_entities()
        self.player = SMSPlayer(self.manager, get_location_tree(), get_location_hierarchy=get_location_hierarchy)
        self.transport = TransportInfo(transport="sms", source="1234", destination="5678")
        initializer.run(self.manager)

    def tearDown(self):
        MangroveTestCase.tearDown(self)


    def test_should_load_all_subjects(self):
        self._register_entities()

        subjects = load_subject_registration_data(self.manager)

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
        define_type(self.manager, self.entity_type)
        define_type(self.manager, ['reporter'])
        self.name_type = DataDictType(self.manager, name='Name', slug='name', primitive_type='string')
        self.telephone_number_type = DataDictType(self.manager, name='telephone_number', slug='telephone_number',
                                                  primitive_type='string')
        rep1 = create_entity(self.manager, ['reporter'], 'rep1')
        rep1.add_data(data=[(MOBILE_NUMBER_FIELD, '1234', self.telephone_number_type),
            (NAME_FIELD, "Test_reporter", self.name_type)], submission=dict(submission_id="2"))


    def _register_entity(self, text):
        form_code, values = KeyBasedSMSParser().parse(text)
        form_model = get_form_model_by_code(self.manager, form_code)
        self.player.accept(self.transport, form_model, values)

    def _register_entities(self):
        self._register_entity('reg .t clinic .s 1 .g 1 1 .n clinic0')
        self._register_entity('reg .t clinic .s 2 .g 21 21 .n clinic1')
        self._register_entity('reg .t clinic .s 3 .g 11 11 .m 12332114 .n clinic2')
        self._register_entity('reg .t clinic .s 4 .d this is a clinic .l pune .n clinic3')
