from unittest import TestCase
from datawinners.accountmanagement.models import TEST_REPORTER_MOBILE_NUMBER
from mangrove.bootstrap import initializer
from mangrove.datastore.database import _delete_db_and_remove_db_manager, get_db_manager
from mangrove.datastore.entity import get_by_short_code_include_voided
from mangrove.form_model.form_model import MOBILE_NUMBER_FIELD, NAME_FIELD
from mangrove.transport import TransportInfo
from mangrove.transport.contract.survey_response import SurveyResponse
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE
from datawinners.project.data_sender_helper import get_data_sender
from datawinners.tests.test_data_utils import register, create_data_dict


class TestDataSenderHelper(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manager = get_db_manager('http://localhost:5984/', 'mangrove-test')
        _delete_db_and_remove_db_manager(cls.manager)
        cls.manager = get_db_manager('http://localhost:5984/', 'mangrove-test')
        initializer._create_views(cls.manager)

        cls.org_id = 'SLX364903'
        cls._prepare_sms_data_senders()
        cls.test_ds_id = get_by_short_code_include_voided(cls.manager, "test", REPORTER_ENTITY_TYPE).id
        deleted_ds = get_by_short_code_include_voided(cls.manager, "del1", REPORTER_ENTITY_TYPE)
        deleted_ds.void()
        cls.deleted_ds_id = deleted_ds.id

    def test_should_return_data_sender_information_send_from_web(self):
        beany_tester_id = get_by_short_code_include_voided(TestDataSenderHelper.manager, "rep1", REPORTER_ENTITY_TYPE).id
        survey_response = SurveyResponse(TestDataSenderHelper.manager, TransportInfo("web", "tester150411@gmail.com", "destination"), owner_uid=beany_tester_id)
        data_sender = get_data_sender(TestDataSenderHelper.manager, survey_response)
        self.assertEqual(("Beany", "rep1"), data_sender)


    def test_should_return_N_A_when_the_data_sender_was_deleted_and_send_from_smart_phone(self):
        survey_response = SurveyResponse(TestDataSenderHelper.manager, TransportInfo("smartPhone", "nobody@gmail.com", "destination"), owner_uid=self.deleted_ds_id)
        data_sender = get_data_sender(TestDataSenderHelper.manager, survey_response)

        self.assertEqual(("M K Gandhi", "del1"), data_sender)

    def test_should_return_data_sender_TESTER_when_send_from_TEST_REPORTER_MOBILE_NUMBER(self):
        survey_response = SurveyResponse(TestDataSenderHelper.manager, TransportInfo("sms", TEST_REPORTER_MOBILE_NUMBER, "destination"),owner_uid=self.test_ds_id)
        data_sender = get_data_sender(TestDataSenderHelper.manager, survey_response)

        self.assertEqual(('TEST', 'test'), data_sender)

    @classmethod
    def _prepare_sms_data_senders(cls):
        phone_number_type = create_data_dict(TestDataSenderHelper.manager, name='Telephone Number', slug='telephone_number',primitive_type='string')
        first_name_type = create_data_dict(TestDataSenderHelper.manager, name='First Name', slug='first_name', primitive_type='string')

        coordinates = {"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]}
        location = [u'Madagascar', u'Menabe', u'Mahabo', u'Beronono']
        register(TestDataSenderHelper.manager, REPORTER_ENTITY_TYPE, [(MOBILE_NUMBER_FIELD, TEST_REPORTER_MOBILE_NUMBER, phone_number_type), (NAME_FIELD, "TEST", first_name_type)], location=location, short_code="test", geometry=coordinates)
        register(TestDataSenderHelper.manager, REPORTER_ENTITY_TYPE, [(MOBILE_NUMBER_FIELD, "1234567890", phone_number_type), (NAME_FIELD, "Beany", first_name_type)],location,"rep1", coordinates)
        register(TestDataSenderHelper.manager, REPORTER_ENTITY_TYPE, [(MOBILE_NUMBER_FIELD, "261332592634", phone_number_type), (NAME_FIELD, "Qingshan", first_name_type)],location=location,short_code="rep2", geometry=coordinates)
        register(TestDataSenderHelper.manager, REPORTER_ENTITY_TYPE, [(MOBILE_NUMBER_FIELD, "4008123123", phone_number_type), (NAME_FIELD, "KFC", first_name_type)], location=location, short_code="rep4", geometry=coordinates)
        register(TestDataSenderHelper.manager, REPORTER_ENTITY_TYPE, [(MOBILE_NUMBER_FIELD, "4008123123", phone_number_type), (NAME_FIELD, "M K Gandhi", first_name_type)], location=location, short_code="del1", geometry=coordinates)

def register_datasender(manager):
    phone_number_type = create_data_dict(manager, name='Telephone Number', slug='telephone_number',primitive_type='string')
    first_name_type = create_data_dict(manager, name='First Name', slug='first_name', primitive_type='string')
    coordinates = {"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]}
    location = [u'Madagascar', u'Menabe', u'Mahabo', u'Beronono']
    register(manager, REPORTER_ENTITY_TYPE, [(MOBILE_NUMBER_FIELD, "1234567890", phone_number_type),
                                                  (NAME_FIELD, "Tester 150411", first_name_type)], location, "rep12",
             coordinates)
    return get_by_short_code_include_voided(manager, "rep12", REPORTER_ENTITY_TYPE).id
