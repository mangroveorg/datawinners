from django.utils.translation import ugettext
from mangrove.form_model.form_model import MOBILE_NUMBER_FIELD, NAME_FIELD
from mangrove.transport import TransportInfo
from mangrove.transport.reporter import REPORTER_ENTITY_TYPE
from mangrove.transport.submissions import Submission
from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase
from messageprovider.messages import SMS, WEB, SMART_PHONE
from project.data_sender import DataSender
from project.helper import  NOT_AVAILABLE_DS, DataSenderHelper
from tests.test_data_utils import register, create_data_dict


class TestDataSenderHelper(MangroveTestCase):

    def setUp(self):
        super(TestDataSenderHelper, self).setUp()
        self.org_id = 'SLX364903'

    def test_should_return_N_A_when_the_data_sender_was_deleted_and_send_from_sms(self):
        submission = Submission(self.manager, TransportInfo("sms", "123123", "destination"))
        data_sender = DataSenderHelper(self.manager).get_data_sender(self.org_id, submission)

        self.assertEqual((NOT_AVAILABLE_DS, None, '123123'), data_sender)

    def test_should_return_data_sender_information_send_from_web(self):
        submission = Submission(self.manager, TransportInfo("web", "tester150411@gmail.com", "destination"))
        data_sender = DataSenderHelper(self.manager).get_data_sender(self.org_id, submission)

        self.assertEqual(("Tester Pune", "admin", "tester150411@gmail.com"), data_sender)

    def test_should_return_N_A_when_the_data_sender_was_deleted_and_send_from_web(self):
        submission = Submission(self.manager, TransportInfo("web", "nobody@gmail.com", "destination"))
        data_sender = DataSenderHelper(self.manager).get_data_sender(self.org_id, submission)

        self.assertEqual((NOT_AVAILABLE_DS, None, 'nobody@gmail.com'), data_sender)

    def test_should_return_N_A_when_the_data_sender_was_deleted_and_send_from_smart_phone(self):
        submission = Submission(self.manager, TransportInfo("smartPhone", "nobody@gmail.com", "destination"))
        data_sender = DataSenderHelper(self.manager).get_data_sender(self.org_id, submission)

        self.assertEqual((NOT_AVAILABLE_DS, None, 'nobody@gmail.com'), data_sender)

    def test_should_return_all_sms_data_senders_that_have_submitted_data(self):
        self._prepare_sms_data_senders()
        FROM_NUMBER1 = '1234567890'
        FROM_NUMBER2 = '261332592634'
        FROM_NUMBER_NOT_EXIST = '434543545'
        TO_NUMBER = '919880734937'
        EMAIL = "a@b.com"
        Submission(self.manager, TransportInfo(SMS, FROM_NUMBER1, TO_NUMBER), "form_code", []).save()
        Submission(self.manager, TransportInfo(SMS, FROM_NUMBER1, TO_NUMBER), "form_code", []).save()
        Submission(self.manager, TransportInfo(SMS, FROM_NUMBER2, TO_NUMBER), "form_code", []).save()
        Submission(self.manager, TransportInfo(SMS, FROM_NUMBER_NOT_EXIST, TO_NUMBER), "form_code", []).save()
        Submission(self.manager, TransportInfo(WEB, EMAIL, "destination"), "form_code", []).save()
        Submission(self.manager, TransportInfo(SMART_PHONE, EMAIL, "destination"), "form_code", []).save()

        data_sender_list = DataSenderHelper(self.manager).get_all_sms_data_senders_with_submission()

        self.assertEqual(3, len(data_sender_list))
        self.assertEqual(DataSender(FROM_NUMBER1, "Beany", "rep1"), data_sender_list[0])
        self.assertEqual(DataSender(FROM_NUMBER2, "Qingshan", "rep2"), data_sender_list[1])
        self.assertEqual(DataSender(FROM_NUMBER_NOT_EXIST, ugettext(NOT_AVAILABLE_DS), None), data_sender_list[2])

    def test_should_return_all_non_sms_data_senders_that_have_submitted_data(self):
        FROM_NUMBER1 = '1234567890'
        TO_NUMBER = '919880734937'
        EMAIL1 = "tester150411@gmail.com"
        EMAIL2 = "mamy@mailinator.com"
        EMAIL_NOT_EXIST = "a@b.c"
        Submission(self.manager, TransportInfo(SMS, FROM_NUMBER1, TO_NUMBER), "form_code", []).save()
        Submission(self.manager, TransportInfo(WEB, EMAIL1, "destination"), "form_code", []).save()
        Submission(self.manager, TransportInfo(SMART_PHONE, EMAIL2, "destination"), "form_code", []).save()
        Submission(self.manager, TransportInfo(SMART_PHONE, EMAIL_NOT_EXIST, "destination"), "form_code", []).save()

        data_sender_list = DataSenderHelper(self.manager).get_all_non_sms_data_senders_with_submission(self.org_id)

        self.assertEqual(3, len(data_sender_list))
        self.assertIn(DataSender(EMAIL1, "Tester Pune", "admin"), data_sender_list)
        self.assertIn(DataSender(EMAIL2, "mamy rasamoel", "rep11"), data_sender_list)
        self.assertIn(DataSender(EMAIL_NOT_EXIST, ugettext(NOT_AVAILABLE_DS), None), data_sender_list)

    def _prepare_sms_data_senders(self):
        phone_number_type = create_data_dict(self.manager, name='Telephone Number', slug='telephone_number',primitive_type='string')
        first_name_type = create_data_dict(self.manager, name='First Name', slug='first_name', primitive_type='string')

        coordinates = {"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]}
        location = [u'Madagascar', u'Menabe', u'Mahabo', u'Beronono']
        register(self.manager, REPORTER_ENTITY_TYPE, [(MOBILE_NUMBER_FIELD, "1234567890", phone_number_type), (NAME_FIELD, "Beany", first_name_type)],location,"rep1", coordinates)
        register(self.manager, REPORTER_ENTITY_TYPE, [(MOBILE_NUMBER_FIELD, "261332592634", phone_number_type),(NAME_FIELD, "Qingshan", first_name_type)],location=location,short_code="rep2", geometry=coordinates)

