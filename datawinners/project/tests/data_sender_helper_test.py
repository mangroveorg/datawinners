from django.utils.translation import ugettext
from datawinners.accountmanagement.models import TEST_REPORTER_MOBILE_NUMBER
from mangrove.form_model.form_model import MOBILE_NUMBER_FIELD, NAME_FIELD, FORM_CODE
from mangrove.transport import TransportInfo
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE
from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase
from datawinners.messageprovider.messages import SMS, WEB, SMART_PHONE
from datawinners.project.data_sender import DataSender
from datawinners.project.data_sender_helper import DataSenderHelper, get_data_sender
from datawinners.project.helper import  NOT_AVAILABLE_DS
from datawinners.tests.test_data_utils import register, create_data_dict
from mangrove.transport.contract.submission import Submission


class TestDataSenderHelper(MangroveTestCase):

    def setUp(self):
        super(TestDataSenderHelper, self).setUp()
        self.org_id = 'SLX364903'
        self._prepare_sms_data_senders()

    def test_should_return_N_A_when_the_data_sender_was_deleted_and_send_from_sms(self):
        submission = Submission(self.manager, TransportInfo("sms", "123123", "destination"))
        data_sender = get_data_sender(self.manager,self.org_id, submission)

        self.assertEqual((NOT_AVAILABLE_DS, None, '123123'), data_sender)

    def test_should_return_data_sender_information_send_from_web(self):
        submission = Submission(self.manager, TransportInfo("web", "tester150411@gmail.com", "destination"))
        data_sender = get_data_sender(self.manager,self.org_id, submission)

        self.assertEqual(("Tester Pune", "admin", "tester150411@gmail.com"), data_sender)

    def test_should_return_N_A_when_the_data_sender_was_deleted_and_send_from_web(self):
        submission = Submission(self.manager, TransportInfo("web", "nobody@gmail.com", "destination"))
        data_sender = get_data_sender(self.manager,self.org_id, submission)

        self.assertEqual((NOT_AVAILABLE_DS, None, 'nobody@gmail.com'), data_sender)

    def test_should_return_N_A_when_the_data_sender_was_deleted_and_send_from_smart_phone(self):
        submission = Submission(self.manager, TransportInfo("smartPhone", "nobody@gmail.com", "destination"))
        data_sender = get_data_sender(self.manager,self.org_id, submission)

        self.assertEqual((NOT_AVAILABLE_DS, None, 'nobody@gmail.com'), data_sender)

    def test_should_return_data_sender_TESTER_when_send_from_TEST_REPORTER_MOBILE_NUMBER(self):
        submission = Submission(self.manager, TransportInfo("sms", TEST_REPORTER_MOBILE_NUMBER, "destination"))
        data_sender = get_data_sender(self.manager,self.org_id, submission)

        self.assertEqual(('TEST', 'n/a', 'TEST'), data_sender)

    def test_should_combine_sources_if_one_reporter_submits_data_from_different_channels(self):
        data_sender1 = DataSender("12313123123", "data_sender1", "rep1")
        data_sender2 = DataSender("data@winners.com", "data_sender1", "rep1")
        data_sender3 = DataSender("14141241414", "data_sender3", "rep3")

        data_senders = DataSenderHelper(self.manager, None)._combine_channels([data_sender1, data_sender2, data_sender3])

        self.assertEqual(2, len(data_senders))
        self.assertIn(["12313123123", "data@winners.com"], map(lambda x: x.source, data_senders))

    def test_should_combine_sources_for_tuple(self):
        data_sender1 = ("data_sender1", "rep1", "12313123123")
        data_sender2 = ("data_sender1", "rep1", "data@winners.com")
        data_sender3 = ("data_sender3", "rep3", "14141241414")

        data_senders_tuple_list = DataSenderHelper(self.manager, None).combine_channels_for_tuple([data_sender1, data_sender2, data_sender3])

        self.assertEqual(2, len(data_senders_tuple_list))
        self.assertIn("12313123123,data@winners.com", map(lambda x: x[-1], data_senders_tuple_list))


    def test_should_return_all_data_senders_that_have_submitted_data(self):
        FROM_NUMBER1 = '1234567890'
        FROM_NUMBER2 = '261332592634'
        FROM_NUMBER_NOT_EXIST = '434543545'
        TO_NUMBER = '919880734937'
        EMAIL = "a@b.com"
        EMAIL1 = "tester150411@gmail.com"
        EMAIL2 = "mamy@mailinator.com"
        EMAIL_NOT_EXIST = "a@b.c"

        Submission(self.manager, TransportInfo(SMS, FROM_NUMBER1, TO_NUMBER), FORM_CODE, []).save()
        Submission(self.manager, TransportInfo(SMS, FROM_NUMBER1, TO_NUMBER), FORM_CODE, []).save()
        Submission(self.manager, TransportInfo(SMS, FROM_NUMBER2, TO_NUMBER), FORM_CODE, []).save()
        Submission(self.manager, TransportInfo(SMS, FROM_NUMBER_NOT_EXIST, TO_NUMBER), FORM_CODE, []).save()
        Submission(self.manager, TransportInfo(WEB, EMAIL, "destination"), FORM_CODE, []).save()
        Submission(self.manager, TransportInfo(WEB, EMAIL, "destination"), FORM_CODE, []).save()
        Submission(self.manager, TransportInfo(SMART_PHONE, EMAIL, "destination"), FORM_CODE, []).save()
        Submission(self.manager, TransportInfo(WEB, EMAIL1, "destination"), FORM_CODE, []).save()
        Submission(self.manager, TransportInfo(SMART_PHONE, EMAIL2, "destination"), FORM_CODE, []).save()
        Submission(self.manager, TransportInfo(SMART_PHONE, EMAIL_NOT_EXIST, "destination"), FORM_CODE, []).save()
        Submission(self.manager, TransportInfo(SMS, TEST_REPORTER_MOBILE_NUMBER, TO_NUMBER), FORM_CODE, []).save()

        Submission(self.manager, TransportInfo(SMS, "4008123123", TO_NUMBER), "sent for other form_code which shouldn't be included in the result", []).save()

        data_sender_list = DataSenderHelper(self.manager, FORM_CODE).get_all_data_senders_ever_submitted(self.org_id)

        self.assertEqual(6, len(data_sender_list))

        self.assertIn(DataSender([FROM_NUMBER1], "Beany", "rep1"), data_sender_list)
        self.assertIn(DataSender([FROM_NUMBER2], "Qingshan", "rep2"), data_sender_list)
        self.assertIn(DataSender([EMAIL1], "Tester Pune", "admin"), data_sender_list)
        self.assertIn(DataSender([TEST_REPORTER_MOBILE_NUMBER], "TEST", "test"), data_sender_list)
        self.assertIn(DataSender(sorted([EMAIL_NOT_EXIST, FROM_NUMBER_NOT_EXIST, EMAIL]), ugettext(NOT_AVAILABLE_DS), None), data_sender_list)
        self.assertIn(DataSender([EMAIL2], "mamy rasamoel", "rep11"), data_sender_list)


    def _prepare_sms_data_senders(self):
        phone_number_type = create_data_dict(self.manager, name='Telephone Number', slug='telephone_number',primitive_type='string')
        first_name_type = create_data_dict(self.manager, name='First Name', slug='first_name', primitive_type='string')

        coordinates = {"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]}
        location = [u'Madagascar', u'Menabe', u'Mahabo', u'Beronono']
        register(self.manager, REPORTER_ENTITY_TYPE, [(MOBILE_NUMBER_FIELD, "1234567890", phone_number_type), (NAME_FIELD, "Beany", first_name_type)],location,"rep1", coordinates)
        register(self.manager, REPORTER_ENTITY_TYPE, [(MOBILE_NUMBER_FIELD, "261332592634", phone_number_type), (NAME_FIELD, "Qingshan", first_name_type)],location=location,short_code="rep2", geometry=coordinates)
        register(self.manager, REPORTER_ENTITY_TYPE, [(MOBILE_NUMBER_FIELD, "4008123123", phone_number_type), (NAME_FIELD, "KFC", first_name_type)], location=location, short_code="rep4", geometry=coordinates)
        register(self.manager, REPORTER_ENTITY_TYPE, [(MOBILE_NUMBER_FIELD, TEST_REPORTER_MOBILE_NUMBER, phone_number_type), (NAME_FIELD, "TEST", first_name_type)], location=location, short_code="test", geometry=coordinates)

