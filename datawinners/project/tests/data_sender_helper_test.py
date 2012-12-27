from mangrove.form_model.form_model import MOBILE_NUMBER_FIELD, NAME_FIELD
from mangrove.transport import TransportInfo
from mangrove.transport.reporter import REPORTER_ENTITY_TYPE
from mangrove.transport.submissions import Submission
from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase
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

    def test_should_get_all_data_senders(self):
        self._prepare_sms_data_senders()
        data_senders = DataSenderHelper(self.manager).get_all_sms_data_senders()
        self.assertEqual(2, len(data_senders))
        self.assertEqual(DataSender("1234567890", "Beany", "rep1"), data_senders[0])
        self.assertEqual(DataSender("261332592634", "Qingshan", "rep2"), data_senders[1])

    def _prepare_sms_data_senders(self):
        phone_number_type = create_data_dict(self.manager, name='Telephone Number', slug='telephone_number',primitive_type='string')
        first_name_type = create_data_dict(self.manager, name='First Name', slug='first_name', primitive_type='string')

        coordinates = {"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]}
        location = [u'Madagascar', u'Menabe', u'Mahabo', u'Beronono']
        register(self.manager, REPORTER_ENTITY_TYPE, [(MOBILE_NUMBER_FIELD, "1234567890", phone_number_type), (NAME_FIELD, "Beany", first_name_type)],location,"rep1", coordinates)
        register(self.manager, REPORTER_ENTITY_TYPE, [(MOBILE_NUMBER_FIELD, "261332592634", phone_number_type),(NAME_FIELD, "Qingshan", first_name_type)],location=location,short_code="rep2", geometry=coordinates)
