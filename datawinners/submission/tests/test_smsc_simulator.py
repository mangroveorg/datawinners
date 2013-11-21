import unittest
from mock import Mock
from datawinners.submission.smsc_simulator import is_data_sender


class TestSMSCSimulator(unittest.TestCase):
    def setUp(self):
        self.org_setting = Mock()
        self.org_setting.document_store = 'hni_testorg_slx364903'

    def test_should_return_true_if_query_with_an_existing_data_sender_mobile_number(self):
        self.assertTrue(is_data_sender('919970059125', self.org_setting))

    def test_should_return_false_if_query_with_a_false_data_sender_mobile_number(self):
        self.assertFalse(is_data_sender('not_a_data_sender_number', self.org_setting))
