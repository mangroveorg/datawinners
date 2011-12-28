# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from collections import OrderedDict
from mangrove.form_model.field import TextField
from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase
from datawinners.entity.import_data import load_subject_registration_data
from datawinners.entity.import_data import FilePlayer
from datawinners.location.LocationTree import get_location_tree
from mangrove.bootstrap import initializer
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.entity import create_entity
from mangrove.datastore.entity_type import define_type
from mangrove.form_model.form_model import MOBILE_NUMBER_FIELD, NAME_FIELD
from mangrove.transport.player.player import SMSPlayer
from mangrove.transport.player.parser import CsvParser
from mangrove.transport.facade import Channel
from mangrove.transport import TransportInfo, Request
from mangrove.transport.submissions import Submission
from mangrove.errors.MangroveException import DataObjectAlreadyExists, MultipleReportersForANumberException
from mangrove.form_model.form_model import FormModel
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
        self.player.accept(Request(text, self.transport))

    def _register_entities(self):
        self._register_entity('reg .t clinic .s 1 .g 1 1 .n clinic0')
        self._register_entity('reg .t clinic .s 2 .g 21 21 .n clinic1')
        self._register_entity('reg .t clinic .s 3 .g 11 11 .m 12332114 .n clinic2')
        self._register_entity('reg .t clinic .s 4 .d this is a clinic .l pune .n clinic3')

def dummy_get_location_hierarchy(foo):
    return [u'arantany']

class DummyLocationTree(object):
    def get_location_hierarchy_for_geocode(self, lat, long ):
        return ['madagascar']

    def get_centroid(self, location_name, level):
        return 60, -12

class TestFilePlayer(MangroveTestCase):

    def setUp(self):
        MangroveTestCase.setUp(self)
        initializer.run(self.manager)

        self.entity_type = ["reporter"]
        self.telephone_number_type = DataDictType(self.manager, name='telephone_number', slug='telephone_number',
                                                  primitive_type='string')
        self.entity_id_type = DataDictType(self.manager, name='Entity Id Type', slug='entity_id', primitive_type='string')
        self.name_type = DataDictType(self.manager, name='Name', slug='name', primitive_type='string')
        self.telephone_number_type.save()
        self.name_type.save()
        self.reporter = create_entity(self.manager, entity_type=self.entity_type,
                                      location=["India", "Pune"], aggregation_paths=None, short_code="rep1",
                                      )
        self.reporter.add_data(data=[(MOBILE_NUMBER_FIELD, '1234', self.telephone_number_type),
            (NAME_FIELD, "Test_reporter", self.name_type)], submission=dict(submission_id="1"))

        question1 = TextField(name="entity_question", code="EID", label="What is associated entity",
                              language="en", entity_question_flag=True, ddtype=self.entity_id_type)
        question2 = TextField(name="Name", code="NAME", label="Clinic Name",
                              defaultValue="some default value", language="eng",
                              ddtype=self.name_type, required=False)
        self.form_model = FormModel(self.manager, entity_type=self.entity_type, name="Dengue", label="Dengue form_model",
                                    form_code="clinic", type='survey', fields=[question1,question2])
        self.form_model.save()

        self.csv_data_for_activity_report = """
                                FORM_CODE,EID,NAME
                                clinic,rep1,XYZ
        """
        self.csv_data_about_reporter = """
                                FORM_CODE,t,n,l,d,m
                                REG,"reporter",Dr. A,Pune,"Description",201
        """
        self.csv_data_with_same_mobile_number = """
                                FORM_CODE,t,n,l,d,m
                                REG,"reporter",Dr. A,Pune,"Description",201
                                REG,"reporter",Dr. B,Pune,"Description",201
        """
        self.csv_data_with_exception = """
                                FORM_CODE,t,n,l,d,m
                                REG,"reporter",Dr. A,Pune,"Description",201
                                REG,"reporter",Dr. B,Pune,"Description",201
                                REG,"reporter",Dr. C,Pune,"Description",202
        """
        self.csv_data_with_missing_name = """
                                FORM_CODE,t,n,l,d,m
                                REG,"reporter",,Pune,"Description",201
        """
        self.parser = CsvParser()
        self.file_player = FilePlayer(self.manager,self.parser, Channel.CSV, DummyLocationTree(),dummy_get_location_hierarchy)

    def tearDown(self):
        MangroveTestCase.tearDown(self)

    def test_should_import_csv_string_if_it_contains_data_about_reporters(self):
        responses = self.file_player.accept(self.csv_data_about_reporter)
        self.assertTrue(responses[0].success)
        submission_log = Submission.get(self.manager, responses[0].submission_id)
        self.assertEquals(True, submission_log. status)
        self.assertEquals("csv", submission_log.channel)
        self.assertEquals("reg", submission_log.form_code)
        self.assertEquals({'t':'reporter', 'n':'Dr. A','l':'Pune','d':'Description','m':'201'}, submission_log.values)

    def test_should_import_csv_string_if_it_contains_data_for_activity_reporters(self):
        responses = self.file_player.accept(self.csv_data_for_activity_report)
        self.assertTrue(responses[0].success)
        submission_log = Submission.get(self.manager, responses[0].submission_id)
        self.assertEquals("csv", submission_log.channel)
        self.assertEquals(u'rep1', responses[0].short_code)

    def test_should_give_error_for_multiple_reporter_with_same_mobile_number(self):
        responses = self.file_player.accept(self.csv_data_with_same_mobile_number)
        self.assertTrue(responses[0].success)
        self.assertFalse(responses[1].success)
        self.assertEqual(u'Sorry, the telephone number 201 has already been registered',responses[1].errors['error'])

    def test_should_import_next_value_if_exception_with_previous(self):
        responses = self.file_player.accept(self.csv_data_with_exception)
        self.assertTrue(responses[0].success)
        self.assertFalse(responses[1].success)
        self.assertTrue(responses[2].success)
        submission_log = Submission.get(self.manager, responses[0].submission_id)
        self.assertEquals({'t':'reporter', 'n':'Dr. A','l':'Pune','d':'Description','m':'201'}, submission_log.values)
        self.assertEquals({'row':{'t':u'reporter', 'n':u'Dr. B','l':[u'arantany'],'d':u'Description','m':u'201','g':'-12 60','s':u'rep3'}, 'error':u'Sorry, the telephone number 201 has already been registered'}, responses[1].errors)
        submission_log = Submission.get(self.manager, responses[2].submission_id)
        self.assertEquals({'t':'reporter', 'n':'Dr. C','l':'Pune','d':'Description','m':'202'}, submission_log.values)

    def test_should_give_error_for_missing_field(self):
        responses = self.file_player.accept(self.csv_data_with_missing_name)
        self.assertFalse(responses[0].success)
        self.assertEqual(OrderedDict([('n', 'Answer for question n is required')]),responses[0].errors['error'])

