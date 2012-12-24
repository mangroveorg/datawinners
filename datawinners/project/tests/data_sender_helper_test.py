from mangrove.transport import TransportInfo
from mangrove.transport.submissions import Submission
from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase
from project.helper import  NOT_AVAILABLE_DS, DataSenderHelper

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