from unittest import TestCase
from mangrove.datastore.documents import EntityDocument, ContactDocument
from datawinners.accountmanagement.models import TEST_REPORTER_MOBILE_NUMBER
from mangrove.bootstrap import initializer
from mangrove.datastore.database import _delete_db_and_remove_db_manager, get_db_manager
from mangrove.datastore.entity import get_by_short_code_include_voided
from mangrove.form_model.form_model import MOBILE_NUMBER_FIELD, NAME_FIELD
from mangrove.transport import TransportInfo
from mangrove.transport.contract.survey_response import SurveyResponse
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE
from datawinners.project.data_sender_helper import get_data_sender
from datawinners.tests.test_data_utils import register
from mangrove.utils.test_utils.database_utils import uniq
from mangrove.datastore.cache_manager import get_cache_manager
import datawinners.search.datasender_index as unused

class TestDataSenderHelper(TestCase):
    @classmethod
    def setUpClass(cls):
        ContactDocument.registered_functions=[]
        database_name = uniq('mangrove-test')
        cls.manager = get_db_manager('http://localhost:5984/', database_name)
        _delete_db_and_remove_db_manager(cls.manager)
        cls.manager = get_db_manager('http://localhost:5984/', database_name)
        initializer._create_views(cls.manager)

        cls.org_id = 'SLX364903'
        cls._prepare_sms_data_senders()
        cls.test_ds_id = get_by_short_code_include_voided(cls.manager, "test", REPORTER_ENTITY_TYPE).id
        deleted_ds = get_by_short_code_include_voided(cls.manager, "del1", REPORTER_ENTITY_TYPE)
        deleted_ds.void()
        cls.deleted_ds_id = deleted_ds.id

    @classmethod
    def tearDownClass(cls):
        _delete_db_and_remove_db_manager(cls.manager)
        get_cache_manager().flush_all()

    def test_should_return_data_sender_information_send_from_web(self):
        beany_tester_id = get_by_short_code_include_voided(TestDataSenderHelper.manager, "rep1",
                                                           REPORTER_ENTITY_TYPE).id
        survey_response = SurveyResponse(TestDataSenderHelper.manager,
                                         TransportInfo("web", "tester150411@gmail.com", "destination"),
                                         owner_uid=beany_tester_id)
        data_sender = get_data_sender(TestDataSenderHelper.manager, survey_response)
        self.assertEqual(("Beany", "rep1", data_sender[2]), data_sender)


    def test_should_return_N_A_when_the_data_sender_was_deleted_and_send_from_smart_phone(self):
        survey_response = SurveyResponse(TestDataSenderHelper.manager,
                                         TransportInfo("smartPhone", "nobody@gmail.com", "destination"),
                                         owner_uid=self.deleted_ds_id)
        data_sender = get_data_sender(TestDataSenderHelper.manager, survey_response)

        self.assertEqual(("M K Gandhi", u"del1"), data_sender[:2])

    def test_should_return_data_sender_TESTER_when_send_from_TEST_REPORTER_MOBILE_NUMBER(self):
        survey_response = SurveyResponse(TestDataSenderHelper.manager,
                                         TransportInfo("sms", TEST_REPORTER_MOBILE_NUMBER, "destination"),
                                         owner_uid=self.test_ds_id)
        data_sender = get_data_sender(TestDataSenderHelper.manager, survey_response)

        self.assertEqual(('TEST', 'test', data_sender[2]), data_sender)

    @classmethod
    def _prepare_sms_data_senders(cls):
        coordinates = {"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]}
        location = [u'Madagascar', u'Menabe', u'Mahabo', u'Beronono']
        register(TestDataSenderHelper.manager, REPORTER_ENTITY_TYPE,
                 [(MOBILE_NUMBER_FIELD, TEST_REPORTER_MOBILE_NUMBER),
                  (NAME_FIELD, "TEST")], location=location, short_code="test", geometry=coordinates)
        register(TestDataSenderHelper.manager, REPORTER_ENTITY_TYPE,
                 [(MOBILE_NUMBER_FIELD, "1234567890"), (NAME_FIELD, "Beany")],
                 location, "rep1", coordinates)
        register(TestDataSenderHelper.manager, REPORTER_ENTITY_TYPE,
                 [(MOBILE_NUMBER_FIELD, "261332592634"), (NAME_FIELD, "Qingshan")],
                 location=location, short_code="rep2", geometry=coordinates)
        register(TestDataSenderHelper.manager, REPORTER_ENTITY_TYPE,
                 [(MOBILE_NUMBER_FIELD, "4008123123"), (NAME_FIELD, "KFC")],
                 location=location, short_code="rep4", geometry=coordinates)
        register(TestDataSenderHelper.manager, REPORTER_ENTITY_TYPE,
                 [(MOBILE_NUMBER_FIELD, "4008123123"), (NAME_FIELD, "M K Gandhi")],
                 location=location, short_code="del1", geometry=coordinates)
